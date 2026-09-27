from pydantic import BaseModel, Field


class AnalyticsResponse(BaseModel):
    total_clicks: int
    clicks_today: int
    clicks_this_week: int
    clicks_this_month: int
    device_breakdown: dict[str, int] = Field(default_factory=dict)
    browser_breakdown: dict[str, int] = Field(default_factory=dict)
    clicks_by_date: dict[str, int] = Field(default_factory=dict)
    referrers: dict[str, int] = Field(default_factory=dict)


class AdminStatistics(BaseModel):
    total_users: int
    active_users: int
    total_urls: int
    active_urls: int
    total_clicks: int
    clicks_today: int
