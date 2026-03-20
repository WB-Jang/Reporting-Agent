"""Report metadata models and the report catalog."""

from dataclasses import dataclass, field
from typing import List, Dict


@dataclass
class ParamSpec:
    """Specification for a single parameter required by a report."""

    name: str
    prompt: str                    # Question shown to the user
    example: str = ""              # Example value shown as hint


@dataclass
class ReportMeta:
    """Metadata describing a single report type."""

    report_id: str
    label: str                     # Human-readable display name
    description: str = ""
    required_params: List[ParamSpec] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Sample report catalog — replace / extend with real entries as needed.
# ---------------------------------------------------------------------------
REPORT_CATALOG: Dict[str, ReportMeta] = {
    "fx5220_1st": ReportMeta(
        report_id="fx5220_1st",
        label="FX5220 (1차)",
        description="외환 FX5220 1차 보고서",
        required_params=[
            ParamSpec("base_date", "기준일자를 입력해 주세요 (YYYY-MM-DD)", "2026-03-19"),
            ParamSpec("data_dir", "원천 파일 폴더 경로를 입력해 주세요", "data/FX_REPORT"),
        ],
    ),
    "fx5220_2nd": ReportMeta(
        report_id="fx5220_2nd",
        label="FX5220 (2차)",
        description="외환 FX5220 2차 보고서",
        required_params=[
            ParamSpec("base_date", "기준일자를 입력해 주세요 (YYYY-MM-DD)", "2026-03-19"),
        ],
    ),
    "fx5260": ReportMeta(
        report_id="fx5260",
        label="FX5260",
        description="외환 FX5260 보고서",
        required_params=[
            ParamSpec("base_date", "기준일자를 입력해 주세요 (YYYY-MM-DD)", "2026-03-19"),
        ],
    ),
    "bok_10days": ReportMeta(
        report_id="bok_10days",
        label="BOK 연체 10일",
        description="한국은행 연체 10일 보고서",
        required_params=[
            ParamSpec("base_date", "기준일자를 입력해 주세요 (YYYY-MM-DD)", "2026-03-19"),
        ],
    ),
    "fss_10days": ReportMeta(
        report_id="fss_10days",
        label="FSS 연체 10일",
        description="금융감독원 연체 10일 보고서",
        required_params=[
            ParamSpec("base_date", "기준일자를 입력해 주세요 (YYYY-MM-DD)", "2026-03-19"),
        ],
    ),
    "corp_loan": ReportMeta(
        report_id="corp_loan",
        label="기업대출",
        description="기업대출 보고서",
        required_params=[
            ParamSpec("base_date", "기준일자를 입력해 주세요 (YYYY-MM-DD)", "2026-03-19"),
            ParamSpec("department", "담당 부서명을 입력해 주세요", "기업금융팀"),
        ],
    ),
    "radars_all": ReportMeta(
        report_id="radars_all",
        label="RADARS (전체)",
        description="RADARS 전체 보고서 (B2901~B2915)",
        required_params=[
            ParamSpec("base_date", "기준일자를 입력해 주세요 (YYYY-MM-DD)", "2026-03-19"),
            ParamSpec("output_dir", "출력 폴더 경로를 입력해 주세요", "data/RADARS"),
        ],
    ),
}
