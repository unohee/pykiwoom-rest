"""키움증권 API 필드명 → LLM-friendly camelCase 변환"""

from typing import Dict


def remap(data: dict, field_map: dict) -> dict:
    """필드명을 LLM-friendly 이름으로 변환. 맵에 없는 키는 제외."""
    return {field_map.get(k, k): v for k, v in data.items() if k in field_map}


def remap_keep_all(data: dict, field_map: dict) -> dict:
    """필드명을 변환하되 맵에 없는 키도 원본 이름으로 유지."""
    return {field_map.get(k, k): v for k, v in data.items()}


# ── 주식 현재가 (ka10001 output) ──
STOCK_PRICE = {
    "stk_cd": "code",
    "stk_nm": "name",
    "cur_prc": "currentPrice",
    "opn_prc": "open",
    "hgh_prc": "high",
    "low_prc": "low",
    "trd_vol": "volume",
    "trd_amt": "tradingValue",
    "prdy_vrss": "change",
    "prdy_ctrt": "changeRate",
    "prdy_vol": "prevVolume",
    "par_prc": "faceValue",
    "lstg_stk_cnt": "listedShares",
    "mkt_cap": "marketCap",
    "per": "per",
    "eps": "eps",
    "pbr": "pbr",
    "bps": "bps",
    "d250_hgpr": "high250d",
    "d250_lwpr": "low250d",
    "stck_prpr": "currentPrice",
    "prdy_vrss_sign": "changeSign",
    "acml_vol": "volume",
    "acml_tr_pbmn": "tradingValue",
    "stck_oprc": "open",
    "stck_hgpr": "high",
    "stck_lwpr": "low",
    "hts_kor_isnm": "name",
}

# ── 호가 (ka10004 output) ──
ORDERBOOK = {
    "stk_cd": "code",
    "stk_nm": "name",
    "askp1": "askPrice1",
    "askp2": "askPrice2",
    "askp3": "askPrice3",
    "askp4": "askPrice4",
    "askp5": "askPrice5",
    "askp6": "askPrice6",
    "askp7": "askPrice7",
    "askp8": "askPrice8",
    "askp9": "askPrice9",
    "askp10": "askPrice10",
    "bidp1": "bidPrice1",
    "bidp2": "bidPrice2",
    "bidp3": "bidPrice3",
    "bidp4": "bidPrice4",
    "bidp5": "bidPrice5",
    "bidp6": "bidPrice6",
    "bidp7": "bidPrice7",
    "bidp8": "bidPrice8",
    "bidp9": "bidPrice9",
    "bidp10": "bidPrice10",
    "askp_rsqn1": "askVolume1",
    "askp_rsqn2": "askVolume2",
    "askp_rsqn3": "askVolume3",
    "askp_rsqn4": "askVolume4",
    "askp_rsqn5": "askVolume5",
    "bidp_rsqn1": "bidVolume1",
    "bidp_rsqn2": "bidVolume2",
    "bidp_rsqn3": "bidVolume3",
    "bidp_rsqn4": "bidVolume4",
    "bidp_rsqn5": "bidVolume5",
    "total_askp_rsqn": "totalAskVolume",
    "total_bidp_rsqn": "totalBidVolume",
}

# ── 차트 OHLCV (ka10080~ka10094 output2 항목) ──
CHART_PRICE = {
    "stck_bsop_date": "date",
    "stck_cntg_hour": "time",
    "stck_oprc": "open",
    "stck_hgpr": "high",
    "stck_lwpr": "low",
    "stck_clpr": "close",
    "acml_vol": "volume",
    "acml_tr_pbmn": "tradingValue",
    "prdy_vrss": "change",
    "prdy_ctrt": "changeRate",
    "opn_prc": "open",
    "hgh_prc": "high",
    "low_prc": "low",
    "cls_prc": "close",
    "trd_vol": "volume",
    "trd_amt": "tradingValue",
    "stk_dt": "date",
}

# ── 순위 공통 (output2 항목) ──
RANKING = {
    "stk_cd": "code",
    "stk_nm": "name",
    "cur_prc": "currentPrice",
    "prdy_vrss": "change",
    "prdy_ctrt": "changeRate",
    "trd_vol": "volume",
    "trd_amt": "tradingValue",
    "acml_vol": "volume",
    "acml_tr_pbmn": "tradingValue",
    "stck_prpr": "currentPrice",
    "hts_kor_isnm": "name",
    "mksc_shrn_iscd": "code",
    "data_rank": "rank",
}

# ── 계좌 잔고 ──
ACCOUNT_BALANCE = {
    "tot_asst_amt": "totalAsset",
    "nass_amt": "netAsset",
    "pchs_amt_smtl": "totalPurchase",
    "evlu_amt_smtl": "totalEval",
    "evlu_pfls_smtl": "totalProfitLoss",
    "evlu_pfls_rt": "profitLossRate",
    "dnca_tot_amt": "depositTotal",
    "scts_evlu_amt": "stockEvalAmount",
    "tot_evlu_amt": "totalEvalAmount",
    "d2_auto_rdpt_amt": "d2AutoRedeem",
}

# ── 보유종목 ──
HOLDING = {
    "pdno": "code",
    "prdt_name": "name",
    "hldg_qty": "quantity",
    "pchs_avg_pric": "avgPrice",
    "pchs_amt": "purchaseAmount",
    "prpr": "currentPrice",
    "evlu_amt": "evalAmount",
    "evlu_pfls_amt": "profitLoss",
    "evlu_pfls_rt": "profitLossRate",
    "stk_cd": "code",
    "stk_nm": "name",
}

# ── 업종 지수 ──
SECTOR_INDEX = {
    "bstp_cls_code": "sectorCode",
    "bstp_cls_nm": "sectorName",
    "bstp_nmix_prpr": "indexPrice",
    "bstp_nmix_prdy_vrss": "change",
    "bstp_nmix_prdy_ctrt": "changeRate",
    "acml_vol": "volume",
    "acml_tr_pbmn": "tradingValue",
    "bstp_nmix_oprc": "open",
    "bstp_nmix_hgpr": "high",
    "bstp_nmix_lwpr": "low",
}

# ── 투자자 매매동향 ──
INVESTOR_TREND = {
    "stk_cd": "code",
    "stk_nm": "name",
    "frgn_ntby_qty": "foreignNetBuy",
    "frgn_ntby_tr_pbmn": "foreignNetBuyAmount",
    "orgn_ntby_qty": "institutionNetBuy",
    "orgn_ntby_tr_pbmn": "institutionNetBuyAmount",
    "prsn_ntby_qty": "personalNetBuy",
    "prsn_ntby_tr_pbmn": "personalNetBuyAmount",
}
