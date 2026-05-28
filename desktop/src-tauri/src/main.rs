/*
Created at: 2026-05-28
Created by: Codex
Last Modified at: 2026-05-28
Last Modified by: Codex
*/
use tauri::{AppHandle, Manager, PhysicalPosition};
use serde::Deserialize;

#[derive(Deserialize)]
struct HttpRequest {
    method: String,
    url: String,
    token: Option<String>,
    body: Option<serde_json::Value>,
}

#[tauri::command]
fn nudge_window(app: AppHandle, dx: i32, dy: i32) -> Result<(), String> {
    let window = app
        .get_webview_window("main")
        .ok_or_else(|| "main_window_missing".to_string())?;
    let position = window.outer_position().map_err(|error| error.to_string())?;
    window
        .set_position(PhysicalPosition::new(position.x + dx, position.y + dy))
        .map_err(|error| error.to_string())
}

#[tauri::command]
fn quit_app(app: AppHandle) {
    app.exit(0);
}

#[tauri::command]
fn open_site(path: Option<String>, base_url: Option<String>) -> Result<(), String> {
    let safe_path = path
        .unwrap_or_else(|| "/".to_string())
        .trim()
        .to_string();
    if safe_path.starts_with("http://") || safe_path.starts_with("https://") {
        return Err("desktop_site_path_invalid".to_string());
    }
    let normalized_path = if safe_path.starts_with('/') {
        safe_path
    } else {
        format!("/{safe_path}")
    };
    let base = base_url.unwrap_or_else(|| "https://hackson.catachess.com".to_string());
    if !is_allowed_site_base(&base) {
        return Err("desktop_site_url_not_allowed".to_string());
    }
    let url = format!("{}{}", base.trim_end_matches('/'), normalized_path);
    open::that(url).map_err(|_| "desktop_site_open_failed".to_string())
}

#[tauri::command]
async fn http_request(payload: HttpRequest) -> Result<serde_json::Value, String> {
    if !is_allowed_api_url(&payload.url) {
        return Err("desktop_api_url_not_allowed".to_string());
    }

    let client = reqwest::Client::new();
    let method = payload
        .method
        .parse::<reqwest::Method>()
        .map_err(|_| "desktop_api_method_invalid".to_string())?;
    let mut request = client.request(method, payload.url);

    if let Some(token) = payload.token.filter(|value| !value.is_empty()) {
        request = request.bearer_auth(token);
    }

    if let Some(body) = payload.body {
        request = request.json(&body);
    }

    let response = request.send().await.map_err(|_| "desktop_api_unreachable".to_string())?;
    let status = response.status();
    let content_type = response
        .headers()
        .get(reqwest::header::CONTENT_TYPE)
        .and_then(|value| value.to_str().ok())
        .unwrap_or("")
        .to_string();
    let text = response.text().await.map_err(|_| "desktop_api_read_failed".to_string())?;

    if !status.is_success() {
        let data = parse_json_or_null(&text);
        return Err(resolve_http_error(status.as_u16(), &data));
    }

    if !content_type.contains("application/json") {
        return Err("desktop_api_non_json_response".to_string());
    }

    let data = if text.trim().is_empty() {
        serde_json::json!(null)
    } else {
        serde_json::from_str(&text).map_err(|_| "desktop_api_non_json_response".to_string())?
    };

    Ok(data)
}

fn parse_json_or_null(text: &str) -> serde_json::Value {
    if text.trim().is_empty() {
        serde_json::json!(null)
    } else {
        serde_json::from_str(text).unwrap_or_else(|_| serde_json::json!(null))
    }
}

fn is_allowed_api_url(url: &str) -> bool {
    [
        "https://hackson.catachess.com/",
        "http://127.0.0.1:18126/",
        "http://127.0.0.1:8000/",
        "http://127.0.0.1:8145/",
    ]
    .iter()
    .any(|prefix| url.starts_with(prefix))
}

fn is_allowed_site_base(base_url: &str) -> bool {
    matches!(
        base_url.trim_end_matches('/'),
        "https://hackson.catachess.com"
            | "http://127.0.0.1:5173"
            | "http://127.0.0.1:8145"
    )
}

fn resolve_http_error(status: u16, data: &serde_json::Value) -> String {
    let detail = match data.get("detail") {
        Some(value) if value.is_string() => value.as_str().unwrap_or("desktop_api_request_failed").to_string(),
        Some(value) if value.is_array() => "desktop_api_validation_failed".to_string(),
        _ => "desktop_api_request_failed".to_string(),
    };
    format!("{status}:{detail}")
}

fn main() {
    tauri::Builder::default()
        .invoke_handler(tauri::generate_handler![nudge_window, quit_app, open_site, http_request])
        .run(tauri::generate_context!())
        .expect("failed to run Hackson Desktop Pet");
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn api_url_allowlist_accepts_known_hackson_sources() {
        assert!(is_allowed_api_url("https://hackson.catachess.com/api/users/me"));
        assert!(is_allowed_api_url("http://127.0.0.1:18126/health"));
        assert!(is_allowed_api_url("http://127.0.0.1:8000/api/work/projects"));
        assert!(is_allowed_api_url("http://127.0.0.1:8145/api/work/projects"));
    }

    #[test]
    fn api_url_allowlist_blocks_unknown_sources() {
        assert!(!is_allowed_api_url("https://example.com/api/users/me"));
        assert!(!is_allowed_api_url("http://127.0.0.1:5173/api/users/me"));
    }

    #[test]
    fn http_error_maps_array_detail_to_validation_code() {
        let data = serde_json::json!({"detail": [{"msg": "Field required"}]});
        assert_eq!(resolve_http_error(422, &data), "422:desktop_api_validation_failed");
    }
}
