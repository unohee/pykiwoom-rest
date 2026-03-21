"""GraphQL SDL 스키마 — LLM introspection용 타입 정의"""

import re

SCHEMA_SDL = '''
"""키움증권 REST API 스키마 (LLM introspection용)"""

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
  """현재가"""
  currentPrice: String!
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
  """PER"""
  per: String
  """EPS"""
  eps: String
  """PBR"""
  pbr: String
  """BPS"""
  bps: String
  """시가총액"""
  marketCap: String
  """250일 고가"""
  high250d: String
  """250일 저가"""
  low250d: String
}

type Orderbook {
  """매도호가 1~10"""
  askPrice1: String
  askPrice2: String
  askPrice3: String
  askPrice4: String
  askPrice5: String
  """매수호가 1~10"""
  bidPrice1: String
  bidPrice2: String
  bidPrice3: String
  bidPrice4: String
  bidPrice5: String
  """매도잔량"""
  askVolume1: String
  askVolume2: String
  askVolume3: String
  """매수잔량"""
  bidVolume1: String
  bidVolume2: String
  bidVolume3: String
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
  """예수금"""
  depositTotal: String
  """주식평가금액"""
  stockEvalAmount: String
  """총평가손익"""
  totalProfitLoss: String
  """손익률"""
  profitLossRate: String
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
  """현재가"""
  currentPrice: String
  """평가금액"""
  evalAmount: String
  """평가손익"""
  profitLoss: String
  """손익률"""
  profitLossRate: String
}

"""계좌 조회 — kiwoom account balance|deposit|eval|orders|executed|profit"""
type Account {
  balance: AccountBalance
  holdings: [Holding!]
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
}

"""업종 조회 — kiwoom sector <code> [--all]"""
type SectorResult {
  code: String
  data: Sector
  allSectors: [Sector!]
}

type InvestorTrend {
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
}

"""투자자 매매동향 — kiwoom investor <code>"""
type InvestorResult {
  code: String!
  data: InvestorTrend
}

"""동적 API 호출 — kiwoom query <domain> <method> [key=value ...]"""
type Query {
  """사용 가능한 도메인: stock, chart, ranking, account, order, sector, investor, program, auth, client"""
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
  hasToken: Boolean!
  isValid: Boolean!
  tokenPrefix: String
  expiresAt: String
  timeToExpiry: Int
  needsRefresh: Boolean
}
'''


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
            m = re.match(r'^(type|enum|input)\s+(\w+)', line)
            if m and m.group(2) == type_name:
                capturing = True
                # 위의 doc comment 포함
                j = i - 1
                docs = []
                while j >= 0 and (lines[j].strip().startswith('"""') or lines[j].strip() == ""):
                    docs.insert(0, lines[j])
                    j -= 1
                result.extend(docs)

        if capturing:
            result.append(line)
            depth += line.count("{") - line.count("}")
            if depth == 0 and "}" in line:
                break

    if result:
        return "\n".join(result).strip()

    # 타입을 못 찾은 경우 — 사용 가능한 타입 목록 반환
    types = re.findall(r'^(?:type|enum|input)\s+(\w+)', SCHEMA_SDL, re.MULTILINE)
    return f"Type '{type_name}' not found. Available: {', '.join(types)}"


def list_types():
    """스키마에 정의된 모든 타입명 반환."""
    return re.findall(r'^(?:type|enum|input)\s+(\w+)', SCHEMA_SDL, re.MULTILINE)
