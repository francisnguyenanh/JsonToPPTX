"""Quick test — render all fixed layouts to output/test_fixed.pptx"""
import sys, os, json
sys.path.insert(0, os.path.dirname(__file__))

from renderer.engine import render_deck

# Semantic intent JSON — exercises Layout F, A, D, C, L with realistic content
deck = {
    "deck_meta": {"theme": "VTI", "lang": "vi", "title": "Test Fixed Layouts"},
    "slides": [
        # Slide 1 — Cover
        {
            "slide_number": 1, "layout": "I", "section_idx": 0,
            "tag": "VTI JAPAN 2026",
            "title": "Hệ Thống Quản Lý Dự Án Tích Hợp AI",
            "subtitle": "Nâng cao hiệu quả vận hành với trí tuệ nhân tạo",
            "caption": "Tháng 5 năm 2026",
            "right_icon_type": "ai"
        },
        # Slide 2 — TOC
        {
            "slide_number": 2, "layout": "J", "section_idx": 0,
            "title": "Nội Dung Trình Bày",
            "left_items": [
                {"section_title": "Tổng quan hệ thống", "slide_range": "3–5"},
                {"section_title": "Tính năng chính", "slide_range": "6–9"},
                {"section_title": "Quy trình triển khai", "slide_range": "10–12"}
            ],
            "right_items": [
                {"section_title": "Kết quả đạt được", "slide_range": "13–15"},
                {"section_title": "Lộ trình phát triển", "slide_range": "16–18"},
                {"section_title": "Kết luận & Hỏi đáp", "slide_range": "19–20"}
            ]
        },
        # Slide 3 — Section Divider
        {
            "slide_number": 3, "layout": "G", "section_idx": 1,
            "section_number": "01",
            "section_title": "Tổng Quan Hệ Thống",
            "subtitle": "Kiến trúc và các thành phần cốt lõi",
            "icon_type": "settings"
        },
        # Slide 4 — Layout F (Narrative with body text + bullets + icon)
        {
            "slide_number": 4, "layout": "F", "section_idx": 1,
            "title": "Kiến Trúc Hệ Thống Tổng Thể",
            "breadcrumb": "Tổng Quan Hệ Thống",
            "body_text": "Hệ thống được xây dựng trên nền tảng microservices hiện đại, tích hợp các công nghệ AI tiên tiến. Kiến trúc cho phép mở rộng linh hoạt theo nhu cầu dự án, đảm bảo tính ổn định và hiệu năng cao trong môi trường sản xuất.",
            "bullets": [
                "Xử lý đồng thời hơn 10.000 yêu cầu mỗi giây",
                "Tích hợp 15+ nguồn dữ liệu khác nhau",
                "Uptime đạt 99.9% trong 12 tháng vận hành"
            ],
            "right_icon_type": "flow",
            "callout_number": "",
            "callout_label": ""
        },
        # Slide 5 — Layout F (Narrative with callout number, no bullets)
        {
            "slide_number": 5, "layout": "F", "section_idx": 1,
            "title": "Hiệu Quả Vận Hành Được Cải Thiện",
            "breadcrumb": "Tổng Quan Hệ Thống",
            "body_text": "Sau 12 tháng triển khai, hệ thống AI đã mang lại những kết quả vượt trội so với mục tiêu ban đầu. Đội ngũ vận hành ghi nhận sự cải thiện đáng kể về năng suất và chất lượng công việc, đặc biệt trong các quy trình phê duyệt và báo cáo định kỳ.",
            "bullets": [],
            "right_icon_type": "chart",
            "callout_number": "87%",
            "callout_label": "Tăng năng suất"
        },
        # Slide 6 — Card Grid 3 cols
        {
            "slide_number": 6, "layout": "A", "section_idx": 1,
            "title": "Các Tính Năng Chính",
            "breadcrumb": "Tổng Quan Hệ Thống",
            "cards": [
                {
                    "header": "Phân tích dữ liệu thông minh",
                    "icon_type": "ai",
                    "bullets": ["Phân tích xu hướng tự động", "Dự báo rủi ro dự án", "Báo cáo tổng hợp realtime"]
                },
                {
                    "header": "Quản lý quy trình tự động",
                    "icon_type": "flow",
                    "bullets": ["Tự động phê duyệt theo ngưỡng", "Thông báo thông minh", "Tích hợp email & Slack"]
                },
                {
                    "header": "Bảo mật & Tuân thủ",
                    "icon_type": "lock",
                    "bullets": ["Xác thực đa nhân tố MFA", "Mã hóa AES-256", "Nhật ký kiểm toán đầy đủ"]
                }
            ]
        },
        # Slide 7 — Two-Column Contrast
        {
            "slide_number": 7, "layout": "D", "section_idx": 1,
            "title": "Trước và Sau Khi Triển Khai AI",
            "breadcrumb": "Kết Quả Đạt Được",
            "left_header": "Phương thức thủ công trước đây",
            "left_bullets": [
                "Xử lý báo cáo mất 3–5 ngày làm việc",
                "Sai sót dữ liệu do nhập tay nhiều lần",
                "Khó kiểm soát tiến độ dự án song song",
                "Thiếu cảnh báo sớm về rủi ro"
            ],
            "right_header": "Hệ thống tích hợp AI hiện tại",
            "right_bullets": [
                "Báo cáo tự động trong vòng 15 phút",
                "Độ chính xác dữ liệu đạt 99.7%",
                "Dashboard realtime cho 50+ dự án",
                "Cảnh báo rủi ro trước 2–3 tuần"
            ]
        },
        # Slide 8 — Flow Steps
        {
            "slide_number": 8, "layout": "C", "section_idx": 1,
            "title": "Quy Trình Triển Khai 4 Bước",
            "breadcrumb": "Quy Trình Triển Khai",
            "flow_direction": "horizontal",
            "steps": [
                {"header": "Khảo sát", "description": "Thu thập yêu cầu và phân tích hệ thống hiện tại"},
                {"header": "Thiết kế", "description": "Xây dựng kiến trúc và lập kế hoạch chi tiết"},
                {"header": "Phát triển", "description": "Lập trình, kiểm thử và tích hợp hệ thống"},
                {"header": "Vận hành", "description": "Go-live, đào tạo người dùng và hỗ trợ liên tục"}
            ]
        },
        # Slide 9 — Data Highlight
        {
            "slide_number": 9, "layout": "E", "section_idx": 1,
            "title": "Kết Quả Đo Lường Sau 12 Tháng",
            "breadcrumb": "Kết Quả Đạt Được",
            "stats": [
                {"number": "87%", "unit": "", "label": "Tăng năng suất đội ngũ"},
                {"number": "3.2×", "unit": "", "label": "Tốc độ xử lý báo cáo"},
                {"number": "99.9%", "unit": "", "label": "Uptime hệ thống"},
                {"number": "↓40%", "unit": "", "label": "Chi phí vận hành"}
            ],
            "context_text": "Các chỉ số được đo lường trong môi trường sản xuất thực tế, với 120 dự án đang hoạt động và hơn 500 người dùng."
        },
        # Slide 10 — Icon Grid
        {
            "slide_number": 10, "layout": "L", "section_idx": 1,
            "title": "Hệ Sinh Thái Công Nghệ",
            "breadcrumb": "Kiến Trúc Hệ Thống",
            "n_cols": 3,
            "cells": [
                {"icon_type": "ai", "label": "AI Engine", "sub_label": "Phân tích & dự báo"},
                {"icon_type": "data", "label": "Data Lake", "sub_label": "Lưu trữ 50TB+"},
                {"icon_type": "flow", "label": "API Gateway", "sub_label": "10K req/giây"},
                {"icon_type": "lock", "label": "Security Layer", "sub_label": "Zero-trust model"},
                {"icon_type": "team", "label": "User Portal", "sub_label": "500+ người dùng"},
                {"icon_type": "chart", "label": "BI Dashboard", "sub_label": "Realtime insights"}
            ]
        },
        # Slide 11 — Timeline
        {
            "slide_number": 11, "layout": "K", "section_idx": 2,
            "title": "Lộ Trình Phát Triển 2026–2027",
            "breadcrumb": "Lộ Trình Phát Triển",
            "events": [
                {"date": "Q1 2026", "label": "Hoàn thiện nền tảng", "description": "Ổn định hệ thống core và tối ưu hiệu năng"},
                {"date": "Q2 2026", "label": "Mở rộng AI", "description": "Tích hợp mô hình LLM cho phân tích văn bản"},
                {"date": "Q3 2026", "label": "Mobile App", "description": "Ra mắt ứng dụng di động iOS & Android"},
                {"date": "Q1 2027", "label": "Mở rộng thị trường", "description": "Triển khai cho 5 khách hàng enterprise mới"}
            ]
        },
        # Slide 12 — Quote
        {
            "slide_number": 12, "layout": "M", "section_idx": 2,
            "title": "Đánh Giá Từ Khách Hàng",
            "breadcrumb": "Phản Hồi",
            "quote_text": "Hệ thống AI của VTI đã thay đổi hoàn toàn cách chúng tôi quản lý dự án. Thời gian họp giảm 60%, quyết định nhanh hơn và chính xác hơn nhờ dữ liệu realtime.",
            "attribution": "— Nguyễn Văn Minh, CTO tại TechCorp Vietnam",
            "context_text": "Phản hồi từ khảo sát độc lập sau 6 tháng sử dụng hệ thống."
        },
        # Slide 13 — CTA
        {
            "slide_number": 13, "layout": "H", "section_idx": 2,
            "heading": "Bước Tiếp Theo",
            "items": [
                {"title": "Demo trực tiếp", "description": "Đặt lịch demo 30 phút với đội ngũ kỹ thuật VTI"},
                {"title": "Pilot 3 tháng", "description": "Triển khai thử nghiệm miễn phí với 1 dự án thực tế"},
                {"title": "Ký kết hợp đồng", "description": "Tùy chỉnh theo nhu cầu và bắt đầu triển khai toàn diện"}
            ]
        }
    ]
}

os.makedirs("output", exist_ok=True)
output_path = "output/test_fixed.pptx"
data = render_deck(deck)
with open(output_path, "wb") as f:
    f.write(data)

print(f"OK - {len(deck['slides'])} slides -> {output_path}")
print(f"   File size: {len(data):,} bytes")
