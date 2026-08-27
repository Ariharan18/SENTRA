"""Streamlit frontend for Phase 3 traffic ingestion."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import pandas as pd
import plotly.express as px
import streamlit as st

from services.api_client import ApiError, TrafficApiClient
from services.config import API_BASE_URL


st.set_page_config(page_title="Smart Traffic Analytics", page_icon="🚦", layout="wide")


def _format_timestamp(value: str | None) -> str:
    if not value:
        return "—"
    return value.replace("T", " ").replace("+00:00", " UTC").replace("Z", " UTC")


def _show_error(error: ApiError) -> None:
    st.error(str(error))


def _require_client() -> TrafficApiClient | None:
    token = st.session_state.get("api_token", "")
    if not token:
        st.info("Enter a user ID or email bearer selector in the sidebar to connect.")
        return None
    return TrafficApiClient(API_BASE_URL, token)


def _reading_table(items: list[dict[str, Any]]) -> None:
    if not items:
        st.info("No traffic readings match the selected filters.")
        return
    rows = []
    for item in items:
        congestion = item.get("congestion") or {}
        rows.append(
            {
                "ID": item.get("id"),
                "Location": item.get("location_id"),
                "Source": item.get("source_id"),
                "Recorded at": _format_timestamp(item.get("recorded_at")),
                "Vehicles": item.get("vehicle_count"),
                "Speed (km/h)": item.get("average_speed_kmh"),
                "Occupancy (%)": item.get("occupancy_percent"),
                "Congestion": congestion.get("congestion_level", "—"),
                "Score": congestion.get("congestion_score", "—"),
            }
        )
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)


def readings_page(client: TrafficApiClient) -> None:
    st.header("Traffic readings")
    st.caption("Readings are loaded and written through FastAPI; the frontend never connects to MySQL.")

    with st.form("reading_filters"):
        first, second, third = st.columns(3)
        with first:
            location_id = st.number_input("Location ID", min_value=0, step=1, value=0)
            city = st.text_input("City")
            date_from = st.date_input("From date", value=None)
        with second:
            source_id = st.number_input("Source ID", min_value=0, step=1, value=0)
            zone = st.text_input("Zone")
            date_to = st.date_input("To date", value=None)
        with third:
            level = st.selectbox("Congestion level", ["All", "Low", "Moderate", "High", "Severe"])
            source_type = st.text_input("Source type")
            page_size = st.selectbox("Rows per page", [10, 25, 50, 100], index=1)
        submitted = st.form_submit_button("Apply filters", type="primary")

    if submitted:
        st.session_state.reading_page = 1
        st.session_state.reading_filters = {
            "location_id": int(location_id) if location_id else None,
            "source_id": int(source_id) if source_id else None,
            "city": city.strip() or None,
            "zone": zone.strip() or None,
            "source": source_type.strip() or None,
            "congestion_level": None if level == "All" else level,
            "date_from": (
                datetime.combine(date_from, datetime.min.time(), tzinfo=timezone.utc).isoformat()
                if date_from
                else None
            ),
            "date_to": (
                datetime.combine(date_to, datetime.max.time(), tzinfo=timezone.utc).isoformat()
                if date_to
                else None
            ),
            "page_size": page_size,
        }

    filters = st.session_state.get(
        "reading_filters",
        {
            "location_id": None,
            "source_id": None,
            "city": None,
            "zone": None,
            "source": None,
            "congestion_level": None,
            "date_from": None,
            "date_to": None,
            "page_size": 25,
        },
    )
    page = st.session_state.get("reading_page", 1)
    params = {"page": page, "page_size": filters["page_size"]}
    params.update({key: value for key, value in filters.items() if key != "page_size" and value is not None})
    try:
        result = client.list_readings(params)
    except ApiError as error:
        _show_error(error)
        return

    st.write(f"Page {result['page']} of {max(1, (result['total'] + result['page_size'] - 1) // result['page_size'])} · {result['total']} total")
    _reading_table(result.get("items", []))
    previous, _, next_page = st.columns([1, 4, 1])
    with previous:
        if st.button("Previous", disabled=page <= 1):
            st.session_state.reading_page = page - 1
            st.rerun()
    with next_page:
        last_page = max(1, (result["total"] + result["page_size"] - 1) // result["page_size"])
        if st.button("Next", disabled=page >= last_page):
            st.session_state.reading_page = page + 1
            st.rerun()


def create_page(client: TrafficApiClient) -> None:
    st.header("Create traffic reading")
    st.caption("All validation is repeated by the FastAPI service.")
    with st.form("create_reading"):
        first, second = st.columns(2)
        with first:
            location_id = st.number_input("Location ID", min_value=1, step=1)
            source_id = st.number_input("Source ID", min_value=1, step=1)
            recorded_at = st.datetime_input("Recorded at (UTC)", value=datetime.now(timezone.utc))
            vehicle_count = st.number_input("Vehicle count", min_value=0, step=1)
            average_speed = st.number_input("Average speed (km/h)", min_value=0.0, step=0.01)
            occupancy = st.number_input("Occupancy (%)", min_value=0.0, max_value=100.0, step=0.01)
        with second:
            st.write("Optional vehicle counts")
            car_count = st.number_input("Cars", min_value=0, step=1)
            bike_count = st.number_input("Bikes", min_value=0, step=1)
            bus_count = st.number_input("Buses", min_value=0, step=1)
            truck_count = st.number_input("Trucks", min_value=0, step=1)
            emergency_count = st.number_input("Emergency vehicles", min_value=0, step=1)
        submitted = st.form_submit_button("Create reading", type="primary")

    if submitted:
        payload = {
            "location_id": int(location_id),
            "source_id": int(source_id),
            "recorded_at": recorded_at.astimezone(timezone.utc).isoformat(),
            "vehicle_count": int(vehicle_count),
            "average_speed_kmh": round(average_speed, 2),
            "occupancy_percent": round(occupancy, 2),
            "car_count": int(car_count),
            "bike_count": int(bike_count),
            "bus_count": int(bus_count),
            "truck_count": int(truck_count),
            "emergency_count": int(emergency_count),
        }
        try:
            result = client.create_reading(payload)
        except ApiError as error:
            _show_error(error)
        else:
            st.success(f"Traffic reading {result.get('id')} created successfully.")
            congestion = result.get("congestion") or {}
            if congestion:
                st.info(f"Congestion: {congestion.get('congestion_level')} (score {congestion.get('congestion_score')})")


def upload_page(client: TrafficApiClient) -> None:
    st.header("CSV upload")
    st.caption("Upload a CSV matching the FastAPI traffic-reading import contract.")
    uploaded = st.file_uploader("Choose a CSV file", type=["csv"])
    if uploaded and st.button("Upload and validate", type="primary"):
        try:
            result = client.upload_readings(uploaded.name, uploaded.getvalue())
        except ApiError as error:
            _show_error(error)
        else:
            st.success(f"Import {result.get('import_id')} completed with status {result.get('status')}.")
            st.write(
                {
                    "Total rows": result.get("total_rows"),
                    "Accepted": result.get("accepted_rows"),
                    "Rejected": result.get("rejected_rows"),
                }
            )
            if result.get("rejected_rows"):
                st.warning("Rejected rows are available on the Import results page.")


def imports_page(client: TrafficApiClient) -> None:
    st.header("Import results")
    page = st.number_input("Import history page", min_value=1, step=1, value=1)
    try:
        result = client.list_imports(int(page))
    except ApiError as error:
        _show_error(error)
        return
    items = result.get("items", [])
    if not items:
        st.info("No imports have been recorded yet.")
        return
    st.dataframe(
        pd.DataFrame(
            [
                {
                    "ID": item.get("import_id"),
                    "File": item.get("file_name"),
                    "Uploaded": _format_timestamp(item.get("uploaded_at")),
                    "Status": item.get("status"),
                    "Total": item.get("total_rows"),
                    "Accepted": item.get("accepted_rows"),
                    "Rejected": item.get("rejected_rows"),
                }
                for item in items
            ]
        ),
        use_container_width=True,
        hide_index=True,
    )
    selected_id = st.selectbox("Inspect import", [item.get("import_id") for item in items])
    if st.button("Load import details"):
        try:
            detail = client.get_import(int(selected_id))
        except ApiError as error:
            _show_error(error)
        else:
            errors = detail.get("errors", [])
            if not errors:
                st.success("This import has no validation errors.")
            else:
                st.warning(f"{len(errors)} rejected row(s)")
                st.dataframe(
                    pd.DataFrame(
                        [
                            {"Row": error.get("row_number"), "Reason": error.get("reason"), "Raw row": error.get("raw_row_json")}
                            for error in errors
                        ]
                    ),
                    use_container_width=True,
                    hide_index=True,
                )


def _analytics_filters() -> dict[str, Any]:
    with st.form("analytics_filter_form"):
        first, second, third = st.columns(3)
        with first:
            date_from = st.date_input("From date", value=None, key="analytics_from")
            location_id = st.number_input("Location ID", min_value=0, step=1, value=0, key="analytics_location")
        with second:
            date_to = st.date_input("To date", value=None, key="analytics_to")
            city = st.text_input("City", key="analytics_city")
        with third:
            zone = st.text_input("Zone", key="analytics_zone")
            source_id = st.number_input("Source ID", min_value=0, step=1, value=0, key="analytics_source")
        source_type = st.text_input("Source type", key="analytics_source_type")
        level = st.selectbox(
            "Congestion level",
            ["All", "Low", "Moderate", "High", "Severe"],
            key="analytics_level",
        )
        submitted = st.form_submit_button("Refresh analytics", type="primary")
    if submitted:
        st.session_state.analytics_filters = {
            "date_from": date_from.isoformat() if date_from else None,
            "date_to": date_to.isoformat() if date_to else None,
            "location_id": int(location_id) if location_id else None,
            "city": city.strip() or None,
            "zone": zone.strip() or None,
            "source_id": int(source_id) if source_id else None,
            "source": source_type.strip() or None,
            "congestion_level": None if level == "All" else level,
        }
    if st.button("Reset filters", key="reset_analytics_filters"):
        st.session_state.pop("analytics_filters", None)
        for key in (
            "analytics_from",
            "analytics_to",
            "analytics_location",
            "analytics_city",
            "analytics_zone",
            "analytics_source",
            "analytics_source_type",
            "analytics_level",
        ):
            st.session_state.pop(key, None)
        st.rerun()
    return st.session_state.get("analytics_filters", {})


def _chart(
    data: Any,
    title: str,
    x: str,
    y: str,
    color: str | None = None,
    key: str | None = None,
) -> None:
    if not data:
        st.info(f"No data available for {title.lower()}.")
        return
    frame = pd.DataFrame(data)
    if x not in frame or y not in frame:
        st.warning(f"The analytics response did not include the fields needed for {title.lower()}.")
        return
    figure = px.bar(frame, x=x, y=y, color=color if color in frame else None, title=title)
    figure.update_layout(margin={"l": 10, "r": 10, "t": 50, "b": 10})
    st.plotly_chart(figure, use_container_width=True, key=key or f"chart-{title.lower().replace(' ', '-')}")


def dashboard_page(client: TrafficApiClient) -> None:
    st.header("Traffic analytics dashboard")
    st.caption("KPIs and visualizations are calculated by FastAPI from the live MySQL dataset.")
    filters = _analytics_filters()
    with st.spinner("Loading analytics..."):
        try:
            summary = client.analytics("summary", filters)
            trends = client.analytics("trends", filters)
            by_location = client.analytics("by-location", filters)
            by_source = client.analytics("vehicle-mix", filters)
            distribution = client.analytics("status-distribution", filters)
            peak_hours = client.analytics("peak-hours", filters)
        except ApiError as error:
            _show_error(error)
            return

    metrics = [
        ("Traffic readings", summary.get("total_readings", summary.get("total_traffic_readings", 0))),
        ("Total vehicles", summary.get("total_vehicle_count", summary.get("traffic_volume", 0))),
        ("Average speed (km/h)", summary.get("average_speed_kmh", 0)),
        ("Severe locations", summary.get("severe_locations", 0)),
    ]
    columns = st.columns(len(metrics))
    for column, (label, value) in zip(columns, metrics):
        column.metric(label, value if value is not None else 0)

    st.subheader("Traffic trends")
    trend_items = trends.get("items", trends.get("data", []))
    if trend_items:
        trend_frame = pd.DataFrame(trend_items)
        x_field = next((field for field in ("period", "date", "recorded_date", "hour") if field in trend_frame), None)
        y_field = next((field for field in ("vehicle_count", "traffic_volume", "total_vehicle_count") if field in trend_frame), None)
        if x_field and y_field:
            st.line_chart(trend_frame.set_index(x_field)[y_field], y_label="Vehicles")
        else:
            st.info("No trend series is available for the selected filters.")
    else:
        st.info("No trend data matches the selected filters.")

    left, right = st.columns(2)
    with left:
        _chart(
            distribution.get("items", distribution.get("data", [])),
            "Congestion distribution",
            "congestion_level",
            "reading_count",
            key="dashboard-congestion-distribution",
        )
    with right:
        location_items = by_location.get("items", by_location.get("data", []))
        location_frame = pd.DataFrame(location_items)
        if not location_frame.empty:
            name_field = next((field for field in ("location_name", "name", "location_id") if field in location_frame), None)
            value_field = next((field for field in ("total_vehicle_count", "vehicle_count", "traffic_volume") if field in location_frame), None)
            if name_field and value_field:
                st.plotly_chart(
                    px.bar(location_frame, x=name_field, y=value_field, title="Traffic by location"),
                    use_container_width=True,
                    key="dashboard-traffic-by-location",
                )
            else:
                st.info("No location comparison is available.")
        else:
            st.info("No location data matches the selected filters.")

    lower_left, lower_right = st.columns(2)
    with lower_left:
        _chart(
            by_source.get("items", by_source.get("data", [])),
            "Vehicle mix",
            "vehicle_type",
            "vehicle_count",
            key="dashboard-vehicle-mix",
        )


def reports_page(client: TrafficApiClient) -> None:
    st.header("Traffic reports")
    st.caption("Report metrics and downloads use the same filters and backend aggregates as the dashboard.")
    filters = _analytics_filters()
    with st.spinner("Preparing report..."):
        try:
            summary = client.analytics("summary", filters)
            trends = client.analytics("trends", filters)
            locations = client.analytics("by-location", filters)
            mix = client.analytics("vehicle-mix", filters)
            distribution = client.analytics("status-distribution", filters)
            peak_hours = client.analytics("peak-hours", filters)
        except ApiError as error:
            _show_error(error)
            return

    st.subheader("Report summary")
    average_count = (
        summary.get("total_vehicle_count", 0) / summary.get("total_readings", 1)
        if summary.get("total_readings")
        else 0
    )
    locations_items = locations.get("items", [])
    peak_items = peak_hours.get("items", [])
    highest = locations_items[0] if locations_items else {}
    peak = peak_items[0] if peak_items else {}
    values = [
        ("Total readings", summary.get("total_readings", 0)),
        ("Total vehicles", summary.get("total_vehicle_count", 0)),
        ("Average vehicle count", round(average_count, 2)),
        ("Average speed (km/h)", summary.get("average_speed_kmh") or 0),
        ("Average congestion", summary.get("average_congestion_score") or 0),
    ]
    for column, (label, value) in zip(st.columns(len(values)), values):
        column.metric(label, value)
    st.write(
        {
            "Highest traffic location": highest.get("location_name", highest.get("location_id", "—")),
            "Peak traffic period": (
                f"hour {peak.get('hour')}, day {peak.get('day_of_week')}"
                if peak
                else "—"
            ),
        }
    )

    left, right = st.columns(2)
    with left:
        _chart(
            distribution.get("items", []),
            "Congestion distribution",
            "congestion_level",
            "reading_count",
            key="reports-congestion-distribution",
        )
    with right:
        _chart(
            mix.get("items", []),
            "Vehicle-type distribution",
            "vehicle_type",
            "vehicle_count",
            key="reports-vehicle-type-distribution",
        )
    _chart(
        locations_items,
        "Location comparison",
        "location_name",
        "total_vehicle_count",
        key="reports-location-comparison",
    )
    _chart(
        peak_items,
        "Peak traffic periods",
        "hour",
        "vehicle_count",
        key="reports-peak-traffic-periods",
    )
    trends_items = trends.get("items", [])
    if trends_items:
        trend_frame = pd.DataFrame(trends_items)
        if "period" in trend_frame and "vehicle_count" in trend_frame:
            st.line_chart(trend_frame.set_index("period")["vehicle_count"], y_label="Vehicles")
    else:
        st.info("No time-based trend data matches the selected filters.")

    st.subheader("Export report data")
    try:
        csv_content, content_type = client.export_analytics(filters)
    except ApiError as error:
        _show_error(error)
    else:
        st.download_button(
            "Download filtered CSV",
            data=csv_content,
            file_name="traffic-analytics-report.csv",
            mime=content_type.split(";")[0],
        )
        st.download_button(
            "Download filtered JSON",
            data=pd.DataFrame(trends_items).to_json(orient="records", date_format="iso"),
            file_name="traffic-analytics-trends.json",
            mime="application/json",
        )
    lower_left, lower_right = st.columns(2)
    with lower_right:
        _chart(
            peak_hours.get("items", peak_hours.get("data", [])),
            "Peak traffic periods",
            "hour",
            "vehicle_count",
            key="reports-peak-traffic-periods-secondary",
        )


st.title("Smart Traffic Analytics")
st.caption("Traffic monitoring and ingestion")
with st.sidebar:
    st.subheader("Connection")
    st.caption(f"FastAPI: {API_BASE_URL}")
    token = st.text_input(
        "Bearer user selector",
        value=st.session_state.get("api_token", ""),
        type="password",
        help="Use an active user ID (for example, 1) or email from the Phase 2 database.",
    )
    if token != st.session_state.get("api_token", ""):
        st.session_state.api_token = token.strip()
        st.session_state.reading_page = 1
    st.divider()
    page_name = st.radio(
        "Navigate",
        ["Analytics dashboard", "Reports", "Traffic readings", "Create reading", "CSV upload", "Import results"],
    )

client = _require_client()
if client:
    if page_name == "Analytics dashboard":
        dashboard_page(client)
    elif page_name == "Reports":
        reports_page(client)
    elif page_name == "Traffic readings":
        readings_page(client)
    elif page_name == "Create reading":
        create_page(client)
    elif page_name == "CSV upload":
        upload_page(client)
    else:
        imports_page(client)
