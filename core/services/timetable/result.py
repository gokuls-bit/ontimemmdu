from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional


@dataclass
class ImportErrorItem:
    sheet: Optional[str] = None
    cell: Optional[str] = None
    row: Optional[int] = None
    column: Optional[int] = None
    section: Optional[str] = None
    day: Optional[str] = None
    period: Optional[int] = None
    raw_value: Optional[str] = None
    error_code: str = "UNSPECIFIED_ERROR"
    message: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "sheet": self.sheet,
            "cell": self.cell,
            "row": self.row,
            "column": self.column,
            "section": self.section,
            "day": self.day,
            "period": self.period,
            "raw_value": self.raw_value,
            "error_code": self.error_code,
            "message": self.message,
        }


@dataclass
class ImportResult:
    success: bool = False
    file_name: str = ""
    semester: str = ""
    imported_count: int = 0
    parsed_count: int = 0
    error_count: int = 0
    warning_count: int = 0
    sections_count: int = 0
    merge_groups_count: int = 0
    laboratories_count: int = 0
    free_periods_count: int = 0
    warnings: List[str] = field(default_factory=list)
    errors: List[Dict[str, Any]] = field(default_factory=list)

    def add_error(
        self,
        error_code: str,
        message: str,
        sheet: Optional[str] = None,
        cell: Optional[str] = None,
        row: Optional[int] = None,
        column: Optional[int] = None,
        section: Optional[str] = None,
        day: Optional[str] = None,
        period: Optional[int] = None,
        raw_value: Optional[str] = None
    ):
        err = ImportErrorItem(
            sheet=sheet,
            cell=cell,
            row=row,
            column=column,
            section=section,
            day=day,
            period=period,
            raw_value=raw_value,
            error_code=error_code,
            message=message
        )
        self.errors.append(err.to_dict())
        self.error_count = len(self.errors)
        self.success = False

    def add_warning(self, warning_message: str):
        self.warnings.append(warning_message)
        self.warning_count = len(self.warnings)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "file_name": self.file_name,
            "semester": self.semester,
            "imported_count": self.imported_count,
            "parsed_count": self.parsed_count,
            "error_count": self.error_count,
            "warning_count": self.warning_count,
            "sections_count": self.sections_count,
            "merge_groups_count": self.merge_groups_count,
            "laboratories_count": self.laboratories_count,
            "free_periods_count": self.free_periods_count,
            "warnings": self.warnings,
            "errors": self.errors,
        }
