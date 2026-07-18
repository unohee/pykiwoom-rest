from unittest.mock import patch

import pytest

from pykiwoom_rest.rate_limit_optimizer import RateLimitOptimizer, SmartRetryStrategy


@pytest.mark.parametrize(
    "kwargs",
    [
        {"burst_capacity": 0},
        {"recovery_time": 0},
        {"request_queue_maxsize": 0},
    ],
)
def test_optimizer_rejects_invalid_constructor_limits(kwargs):
    with pytest.raises(ValueError):
        RateLimitOptimizer(**kwargs)


def test_credential_selection_and_acquisition_edge_cases(monkeypatch):
    empty = RateLimitOptimizer(credentials_list=[])
    assert empty.get_optimal_credential() == (-1, None)
    assert empty.acquire_token_result() == (False, None)

    optimizer = RateLimitOptimizer(credentials_list=[{"APPKEY": "key", "APPSECRET": "secret"}])
    assert optimizer.acquire_token_result(-1) == (False, None)
    bucket = optimizer.token_buckets["key_0"]
    bucket.update({"is_blocked": True, "block_until": None})
    assert optimizer.get_optimal_credential() == (-1, None)
    bucket.update({"is_blocked": True, "block_until": 1})
    assert optimizer.get_optimal_credential()[0] == 0

    bucket["tokens"] = 0
    bucket["last_refill"] = 0
    monkeypatch.setattr("pykiwoom_rest.rate_limit_optimizer.time.sleep", lambda _: None)
    with patch("pykiwoom_rest.rate_limit_optimizer.time.time", side_effect=[0, 0, 1, 1, 1, 1]):
        assert optimizer.acquire_token(0)


def test_bucket_and_error_reset_edge_paths():
    optimizer = RateLimitOptimizer(credentials_list=[{"APPKEY": "key", "APPSECRET": "secret"}])
    bucket = optimizer.token_buckets["key_0"]
    bucket["tokens"] = 2
    bucket["last_refill"] = 0
    with patch("pykiwoom_rest.rate_limit_optimizer.time.time", return_value=1):
        optimizer._refill_tokens(bucket)
    assert bucket["tokens"] == 22
    assert optimizer._calculate_wait_time({"tokens": 1}) == 0
    optimizer.handle_429_error(-1)
    optimizer.reset_error_count(-1)


def test_all_blocked_selection_and_optimization_failures(monkeypatch):
    optimizer = RateLimitOptimizer(
        credentials_list=[{"APPKEY": "one"}, {"APPKEY": "two"}], enable_rotation=True
    )
    for index, credential in enumerate(optimizer.credentials_list):
        optimizer.token_buckets[f"{credential['APPKEY']}_{index}"].update(
            is_blocked=True, block_until=100
        )
    monkeypatch.setattr("pykiwoom_rest.rate_limit_optimizer.time.time", lambda: 1)
    assert optimizer.get_optimal_credential() == (-1, None)
    optimizer.token_buckets["one_0"]["block_until"] = None
    assert optimizer.get_optimal_credential() == (-1, None)
    with pytest.raises(RuntimeError, match="No credentials"):
        RateLimitOptimizer().optimize_request_pattern([{"endpoint": "/x"}])


def test_queue_retry_full_callback_and_context_manager(monkeypatch):
    optimizer = RateLimitOptimizer(credentials_list=[{"APPKEY": "key"}], request_queue_maxsize=1)
    failed = []
    request = {"error_callback": failed.append, "max_retries": 0}
    optimizer._retry_or_fail_queue_request(request, 1, "failed")
    assert failed == [request]

    optimizer.request_queue.put((0, 1, 0, {}))
    full_request = {"error_callback": failed.append}
    assert optimizer.add_request_to_queue(full_request, timeout=0) is False
    assert failed[-1] is full_request
    assert optimizer.stop_queue_processor(timeout=0.01)
    with optimizer as entered:
        assert entered is optimizer


def test_retry_invalid_header_uses_backoff(monkeypatch):
    monkeypatch.setattr("pykiwoom_rest.rate_limit_optimizer.random.uniform", lambda *_: 0)
    assert SmartRetryStrategy().calculate_retry_delay(503, 1, {"Retry-After": "invalid"}) == 7.5


def test_queue_worker_success_callback_and_retry_paths(monkeypatch):
    optimizer = RateLimitOptimizer(credentials_list=[{"APPKEY": "key"}])
    callbacks = []

    def success_callback(request):
        callbacks.append(request)
        optimizer._stop_queue_processor.set()

    request = {"credential_idx": 0, "callback": success_callback}
    optimizer.request_queue.put((0, 1, 0, request))
    monkeypatch.setattr(optimizer, "acquire_token", lambda *_: True)
    optimizer._process_request_queue()
    assert callbacks == [request]

    optimizer._stop_queue_processor.clear()
    failed = {"max_retries": 0, "error_callback": lambda request: optimizer._stop_queue_processor.set()}
    optimizer.request_queue.put((0, 1, 1, failed))
    monkeypatch.setattr(optimizer, "acquire_token", lambda *_: False)
    optimizer._process_request_queue()


def test_queue_due_item_wait_and_retry_enqueue(monkeypatch):
    optimizer = RateLimitOptimizer(credentials_list=[{"APPKEY": "key"}])
    waits = []
    optimizer.request_queue.put((10, 1, 0, {}))
    monkeypatch.setattr("pykiwoom_rest.rate_limit_optimizer.time.time", lambda: 0)
    monkeypatch.setattr(optimizer.request_queue.not_empty, "wait", lambda timeout: (waits.append(timeout), optimizer._stop_queue_processor.set()))
    with pytest.raises(__import__("queue").Empty):
        optimizer._get_next_due_queue_item(timeout=1)
    assert waits == [1]

    optimizer._stop_queue_processor.clear()
    request = {"max_retries": 1}
    monkeypatch.setattr(optimizer, "_calculate_queue_retry_delay", lambda _: 0)
    optimizer._retry_or_fail_queue_request(request, 1, "retry")
    assert request["_retry_count"] == 1
    assert optimizer.request_queue.get_nowait()[-1] is request


def test_optimizer_remaining_selection_token_and_adaptive_paths(monkeypatch):
    optimizer = RateLimitOptimizer(credentials_list=[{"APPKEY": "one"}, {"APPKEY": "two"}], enable_rotation=True)
    first = optimizer.token_buckets["one_0"]
    first.update(is_blocked=True, block_until=0, consecutive_errors=2)
    monkeypatch.setattr("pykiwoom_rest.rate_limit_optimizer.time.time", lambda: 1)
    assert optimizer.get_optimal_credential()[0] in {0, 1}

    first["tokens"] = 0
    optimizer.token_buckets["two_1"]["tokens"] = 1
    assert optimizer._calculate_wait_time({"tokens": 0, "consecutive_errors": 1}) > 0

    optimizer.adaptive_rate_adjustment(0.99)
    optimizer.adaptive_rate_adjustment(0.5)
    with pytest.raises(ValueError):
        optimizer.adaptive_rate_adjustment(float("nan"))


def test_queue_thread_start_duplicate_join_and_callback_failures(monkeypatch):
    optimizer = RateLimitOptimizer(credentials_list=[{"APPKEY": "key"}])
    thread = __import__("unittest").mock.MagicMock()
    thread.is_alive.return_value = True
    optimizer.queue_processor_thread = thread
    optimizer.start_queue_processor()
    thread.start.assert_not_called()
    thread.is_alive.return_value = False
    optimizer.stop_queue_processor(timeout=0.01)
    assert optimizer.join_queue_processor(timeout=0.01)

    failed = []
    request = {"callback": lambda _: (_ for _ in ()).throw(RuntimeError("callback")), "max_retries": 0,
               "error_callback": failed.append}
    optimizer.request_queue.put((0, 1, 0, request))
    optimizer._stop_queue_processor.clear()
    monkeypatch.setattr(optimizer, "acquire_token", lambda *_: True)
    optimizer._process_request_queue = optimizer._process_request_queue

    def due_item(timeout=1):
        optimizer._stop_queue_processor.set()
        return optimizer.request_queue.get_nowait()

    monkeypatch.setattr(optimizer, "_get_next_due_queue_item", due_item)
    optimizer._process_request_queue()
    assert failed == [request]


def test_rate_selection_refill_history_stats_and_optimization_edges(monkeypatch):
    single = RateLimitOptimizer(credentials_list=[{"APPKEY": "key"}])
    bucket = single.token_buckets["key_0"]
    bucket.update(is_blocked=True, block_until=10)
    monkeypatch.setattr("pykiwoom_rest.rate_limit_optimizer.time.time", lambda: 1)
    assert single.get_optimal_credential() == (-1, None)
    bucket.update(is_blocked=True, block_until=0.5, consecutive_errors=2)
    assert single.get_optimal_credential()[0] == 0
    assert bucket["is_blocked"] is False

    rotating = RateLimitOptimizer(credentials_list=[{"APPKEY": "one"}, {"APPKEY": "two"}], enable_rotation=True)
    rotating.get_optimal_credential = lambda: (-1, None)
    assert rotating.acquire_token_result() == (False, None)
    rotating.get_optimal_credential = RateLimitOptimizer.get_optimal_credential.__get__(rotating)
    key = "one_0"
    rotating.token_buckets[key].update(tokens=2, last_refill=0)
    rotating.request_history[key].extend(range(100))
    assert rotating.acquire_token_result(0) == (True, 0)
    assert len(rotating.request_history[key]) == 100

    rotating.token_buckets[key].update(is_blocked=True, block_until=0.5, consecutive_errors=2)
    assert rotating.get_stats()["active_credentials"] == 2
    rotating.token_buckets[key].update(tokens=0, is_blocked=True, block_until=10)
    rotating.token_buckets["two_1"].update(tokens=0, is_blocked=True, block_until=10)
    rotating.get_optimal_credential = lambda: (-1, None)
    with pytest.raises(RuntimeError, match="No available"):
        rotating.optimize_request_pattern([{"endpoint": "/x"}])


def test_queue_start_full_retry_and_callback_error_paths(monkeypatch):
    optimizer = RateLimitOptimizer(credentials_list=[{"APPKEY": "key"}])
    thread = __import__("unittest").mock.MagicMock()
    thread.is_alive.return_value = False
    with patch("pykiwoom_rest.rate_limit_optimizer.threading.Thread", return_value=thread):
        optimizer.start_queue_processor()
    thread.start.assert_called_once()

    optimizer.request_queue = __import__("queue").PriorityQueue(maxsize=1)
    optimizer.request_queue.put((0, 0, 0, {}))
    failed = []
    optimizer._retry_or_fail_queue_request({"max_retries": 1, "error_callback": failed.append}, 1, "retry")
    assert failed
    optimizer._retry_or_fail_queue_request(
        {"max_retries": 0, "error_callback": lambda _: (_ for _ in ()).throw(RuntimeError("bad"))}, 1, "fail"
    )


def test_blocked_token_wait_and_expired_optimization_paths(monkeypatch):
    optimizer = RateLimitOptimizer(credentials_list=[{"APPKEY": "key"}])
    bucket = optimizer.token_buckets["key_0"]
    bucket.update(tokens=0, is_blocked=True, block_until=10, last_refill=1)
    monkeypatch.setattr("pykiwoom_rest.rate_limit_optimizer.time.time", lambda: 1)

    def release(_):
        bucket.update(tokens=1, is_blocked=False, block_until=None, last_refill=1)

    monkeypatch.setattr("pykiwoom_rest.rate_limit_optimizer.time.sleep", release)
    assert optimizer.acquire_token(0) is True

    bucket.update(tokens=0, is_blocked=True, block_until=None)
    assert optimizer.acquire_token_result(0) == (False, None)
    bucket.update(tokens=1, is_blocked=True, block_until=0.5, consecutive_errors=3)
    assert optimizer.optimize_request_pattern([{"endpoint": "/x"}])[0]["credential_idx"] == 0


def test_final_rate_optimizer_queue_and_rotation_boundaries(monkeypatch):
    optimizer = RateLimitOptimizer(credentials_list=[{"APPKEY": "one"}, {"APPKEY": "two"}], enable_rotation=True)
    monkeypatch.setattr("pykiwoom_rest.rate_limit_optimizer.time.time", lambda: 1)
    one = optimizer.token_buckets["one_0"]
    two = optimizer.token_buckets["two_1"]
    one.update(tokens=0, last_refill=1)
    two.update(tokens=1, last_refill=1)
    optimizer.get_optimal_credential = lambda: (0, optimizer.credentials_list[0])
    assert optimizer.acquire_token_result() == (True, 1)

    one.update(tokens=1, last_refill=1, is_blocked=True, block_until=0.5, consecutive_errors=2)
    assert optimizer.acquire_token_result(0) == (True, 0)
    one.update(is_blocked=True, block_until=None)
    two.update(is_blocked=True, block_until=None)
    optimizer.get_optimal_credential = RateLimitOptimizer.get_optimal_credential.__get__(optimizer)
    assert optimizer.get_optimal_credential() == (-1, None)

    queued = RateLimitOptimizer(credentials_list=[{"APPKEY": "key"}])
    assert queued.add_request_to_queue({}) is True
    queued.request_queue.get_nowait()

    def empty_then_stop(timeout=1):
        queued._stop_queue_processor.set()
        raise __import__("queue").Empty

    monkeypatch.setattr(queued, "_get_next_due_queue_item", empty_then_stop)
    queued._stop_queue_processor.clear()
    queued._process_request_queue()

    queued._stop_queue_processor.clear()
    queued.request_queue.put((0, 1, 0, {}))

    def due_item(timeout=1):
        return queued.request_queue.get_nowait()

    def fail_token(*args):
        queued._stop_queue_processor.set()
        raise RuntimeError("worker")

    monkeypatch.setattr(queued, "_get_next_due_queue_item", due_item)
    monkeypatch.setattr(queued, "acquire_token", fail_token)
    queued._process_request_queue()


def test_empty_due_queue_waits_then_exits(monkeypatch):
    optimizer = RateLimitOptimizer(credentials_list=[{"APPKEY": "key"}])
    waits = []

    def stop_after_wait(timeout):
        waits.append(timeout)
        optimizer._stop_queue_processor.set()

    monkeypatch.setattr(optimizer.request_queue.not_empty, "wait", stop_after_wait)
    with pytest.raises(__import__("queue").Empty):
        optimizer._get_next_due_queue_item(timeout=0.01)
    assert waits == [0.01]
