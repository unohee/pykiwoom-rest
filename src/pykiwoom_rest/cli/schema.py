"""GraphQL SDL 스키마 — LLM 탐색용 타입 정의."""

import re


class SchemaTypeNotFound(ValueError):
    """요청한 SDL 타입이 없을 때 발생하는 예외."""

    def __init__(self, type_name, types):
        self.available = types
        super().__init__(f"타입 '{type_name}'을 찾을 수 없습니다. 사용 가능: {', '.join(types)}")


SCHEMA_SDL = '''
"""키움증권 REST API 스키마 (LLM 탐색용)"""

scalar JSON

type Stock {
  """종목코드 (예: 005930)"""
  code: String!
  """종목명"""
  name: String
  """현재가 정보 — kiwoom price <code>"""
  price: StockPrice
  """호가 (매수/매도 10호가) — kiwoom price <code> --orderbook"""
  orderbook: Orderbook
}

type StockPrice {
  """종목코드"""
  code: String
  """종목명"""
  name: String
  """현재가"""
  currentPrice: String!
  """전일대비 부호"""
  changeSign: String
  """전일대비"""
  change: String
  """등락률 (%)"""
  changeRate: String
  """시가"""
  open: String
  """고가"""
  high: String
  """저가"""
  low: String
  """누적거래량"""
  volume: String
  """누적거래대금"""
  tradingValue: String
  """기준가"""
  basePrice: String
  """상한가"""
  upperLimit: String
  """하한가"""
  lowerLimit: String
  """액면가"""
  faceValue: String
  """자본금"""
  capital: String
  """PER"""
  per: String
  """EPS"""
  eps: String
  """PBR"""
  pbr: String
  """BPS"""
  bps: String
  """ROE"""
  roe: String
  """EV"""
  ev: String
  """매출액"""
  revenue: String
  """영업이익"""
  operatingProfit: String
  """당기순이익"""
  netIncome: String
  """시가총액"""
  marketCap: String
  """시가총액 비중"""
  marketCapWeight: String
  """유동주식"""
  floatingShares: String
  """상장주식수"""
  listedShares: String
  """유동비율"""
  floatingRate: String
  """외국인소진율"""
  foreignOwnershipRate: String
  """신용비율"""
  creditRate: String
  """250일 고가"""
  high250d: String
  """250일 저가"""
  low250d: String
  """250일 고가일"""
  high250dDate: String
  """250일 저가일"""
  low250dDate: String
  """연중 최고가"""
  yearHigh: String
  """연중 최저가"""
  yearLow: String
  """예상체결가"""
  expectedPrice: String
  """예상체결량"""
  expectedVolume: String
  """결산월"""
  settlementMonth: String
  """대용가"""
  replacementPrice: String
}

type Orderbook {
  """종목코드"""
  code: String
  """종목명"""
  name: String
  """매도호가 1~10"""
  askPrice1: String
  askPrice2: String
  askPrice3: String
  askPrice4: String
  askPrice5: String
  askPrice6: String
  askPrice7: String
  askPrice8: String
  askPrice9: String
  askPrice10: String
  """매수호가 1~10"""
  bidPrice1: String
  bidPrice2: String
  bidPrice3: String
  bidPrice4: String
  bidPrice5: String
  bidPrice6: String
  bidPrice7: String
  bidPrice8: String
  bidPrice9: String
  bidPrice10: String
  """매도잔량"""
  askVolume1: String
  askVolume2: String
  askVolume3: String
  askVolume4: String
  askVolume5: String
  askVolume6: String
  askVolume7: String
  askVolume8: String
  askVolume9: String
  askVolume10: String
  """매수잔량"""
  bidVolume1: String
  bidVolume2: String
  bidVolume3: String
  bidVolume4: String
  bidVolume5: String
  bidVolume6: String
  bidVolume7: String
  bidVolume8: String
  bidVolume9: String
  bidVolume10: String
  """총매도잔량"""
  totalAskVolume: String
  """총매수잔량"""
  totalBidVolume: String
}

type ChartCandle {
  """날짜 (YYYYMMDD)"""
  date: String!
  """시간 (HHmmss, 분봉만)"""
  time: String
  """체결시각 (YYYYMMDDHHmmss, 분봉/틱)"""
  timestamp: String
  """시가"""
  open: String
  """고가"""
  high: String
  """저가"""
  low: String
  """종가"""
  close: String
  """거래량"""
  volume: String
  """거래대금"""
  tradingValue: String
  """전일대비"""
  change: String
  """전일대비 부호"""
  changeSign: String
  """등락률"""
  changeRate: String
  """회전율"""
  turnoverRate: String
}

"""차트 조회 — kiwoom chart <code> --minute/--daily/--weekly/--monthly/--yearly"""
type Chart {
  code: String!
  type: String!
  data: [ChartCandle!]
}

type Ranking {
  """순위"""
  rank: String
  """종목코드"""
  code: String!
  """종목명"""
  name: String
  """현재가"""
  currentPrice: String
  """전일대비"""
  change: String
  """등락률"""
  changeRate: String
  """거래량"""
  volume: String
  """거래대금"""
  tradingValue: String
}

"""순위 조회 — kiwoom rank volume|amount|gainers|foreign-buy|surge"""
type RankingResult {
  type: String!
  market: String
  items: [Ranking!]
}

type AccountBalance {
  """총자산"""
  totalAsset: String
  """순자산"""
  netAsset: String
  """총매입금액"""
  totalPurchase: String
  """총평가금액"""
  totalEval: String
  """예수금"""
  depositTotal: String
  """주식평가금액"""
  stockEvalAmount: String
  """총평가금액"""
  totalEvalAmount: String
  """추정예탁자산"""
  estimatedDepositAsset: String
  """총평가손익"""
  totalProfitLoss: String
  """손익률"""
  profitLossRate: String
  """D+2 자동상환금액"""
  d2AutoRedeem: String
  """총대출금"""
  totalLoan: String
  """총융자금액"""
  totalCreditLoan: String
  """총대주금액"""
  totalCreditShortLoan: String
}

type Holding {
  """종목코드"""
  code: String!
  """종목명"""
  name: String
  """보유수량"""
  quantity: String
  """매입평균가"""
  avgPrice: String
  """매입금액"""
  purchaseAmount: String
  """전일종가"""
  previousClose: String
  """현재가"""
  currentPrice: String
  """매매가능수량"""
  tradableQuantity: String
  """평가금액"""
  evalAmount: String
  """평가손익"""
  profitLoss: String
  """손익률"""
  profitLossRate: String
}

"""계좌 조회 — kiwoom account balance|deposit|eval|orders|executed|profit"""
type Account {
  type: String!
  summary: AccountBalance
  holdings: [Holding!]
  deposit: JSON
  evaluation: JSON
  unfilledOrders: JSON
  executedOrders: JSON
  profit: JSON
}

type Sector {
  """업종코드"""
  sectorCode: String!
  """업종명"""
  sectorName: String
  """업종지수"""
  indexPrice: String
  """전일대비"""
  change: String
  """등락률"""
  changeRate: String
  """거래량"""
  volume: String
  """거래대금"""
  tradingValue: String
  """시가"""
  open: String
  """고가"""
  high: String
  """저가"""
  low: String
}

"""업종 조회 — kiwoom sector <code> [--all]"""
type SectorResult {
  type: String
  code: String
  data: Sector
  items: [Sector!]
}

type InvestorTrend {
  """종목코드"""
  code: String
  """종목명"""
  name: String
  """날짜"""
  date: String
  """종가"""
  close: String
  """전일대비"""
  change: String
  """거래량"""
  volume: String
  """외국인 순변동"""
  foreignNetChange: String
  """외국인 보유수량"""
  foreignHolding: String
  """외국인 보유비중"""
  foreignOwnership: String
  """외국인 매수가능수량"""
  foreignBuyableShares: String
  """외국인 한도수량"""
  foreignLimit: String
  """외국인 한도소진율"""
  foreignLimitRate: String
  """외국인 순매수"""
  foreignNetBuy: String
  """외국인 순매수금액"""
  foreignNetBuyAmount: String
  """기관 순매수"""
  institutionNetBuy: String
  """기관 순매수금액"""
  institutionNetBuyAmount: String
  """개인 순매수"""
  personalNetBuy: String
  """개인 순매수금액"""
  personalNetBuyAmount: String
}

"""투자자 매매동향 — kiwoom investor <code>"""
type InvestorResult {
  code: String!
  data: InvestorTrend
  items: [InvestorTrend!]
}

"""동적 API 호출 — kiwoom query <domain> <method> [key=value ...]"""
type Query {
  """사용 가능한 도메인: stock, chart, ranking, account, sector, investor, program"""
  domains: [String!]
}

"""주문 — kiwoom order buy|sell <code> --qty N --price N"""
type Order {
  """주문번호"""
  orderNo: String
  """종목코드"""
  code: String
  """주문수량"""
  quantity: Int
  """주문가격"""
  price: Int
  """주문유형"""
  orderType: String
}

"""토큰 상태 — kiwoom token"""
type TokenStatus {
  has_token: Boolean!
  is_valid: Boolean!
  token_prefix: String
  expires_at: String
  time_to_expiry: Int
  needs_refresh: Boolean
}
'''


def validate_schema_sdl():
    """GraphQL SDL description terminator 검증."""
    for line_no, line in enumerate(SCHEMA_SDL.splitlines(), start=1):
        stripped = line.strip()
        if stripped.startswith('"""') and stripped.count('"""') != 2:
            raise ValueError(f"Unterminated SDL description at line {line_no}: {line}")


validate_schema_sdl()


def get_schema(type_name=None):
    """스키마 반환. type_name이 지정되면 해당 타입만 추출."""
    if not type_name:
        return SCHEMA_SDL.strip()

    lines = SCHEMA_SDL.split("\n")
    result = []
    capturing = False
    depth = 0

    for i, line in enumerate(lines):
        if not capturing:
            m = re.match(r"^(type|enum|input|scalar)\s+(\w+)", line)
            if m and m.group(2) == type_name:
                capturing = True
                scalar_type = m.group(1) == "scalar"
                # 인접한 doc comment만 포함 (blank line 너머 root/schema 설명 제외)
                j = i - 1
                docs = []
                while j >= 0 and lines[j].strip().startswith('"""'):
                    docs.insert(0, lines[j])
                    j -= 1
                result.extend(docs)

        if capturing:
            result.append(line)
            if scalar_type:
                break
            depth += line.count("{") - line.count("}")
            if depth == 0 and "}" in line:
                break

    if result:
        return "\n".join(result).strip()

    types = list_types()
    raise SchemaTypeNotFound(type_name, types)


def list_types():
    """스키마에 정의된 모든 타입명 반환."""
    return re.findall(r"^(?:type|enum|input|scalar)\s+(\w+)", SCHEMA_SDL, re.MULTILINE)
