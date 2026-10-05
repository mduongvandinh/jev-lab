# Mẫu áp dụng Jev và ý tưởng thí nghiệm

Jev trả lời ba kiểu câu hỏi: **Noul** (xác suất có/không), **Choice** (chọn một nhãn, kèm xác suất từng nhãn), **Score** (chấm theo mức có thứ tự).
Dưới đây là các mẫu đã dùng thật trong repo, rồi tới danh sách ý tưởng để làm tiếp.

## 9 mẫu đã thử

| Mẫu | Làm gì | Ví dụ trong repo | Cookbook |
|---|---|---|---|
| Gắn nhãn hàng loạt | Mọi câu của một mục trong một request | Mỗi ngày thời tiết 4 câu; mỗi khiếu nại 5 câu | Parallel questions |
| Chấm điểm để xếp hạng | Dùng Noul/Score làm điểm sắp xếp | Khả năng thành bàn của từng cú sút | Re-ranking |
| Phân loại theo cây | Cấp 1 rồi mới hỏi cấp 2 trong nhánh | Hệ thống xe → lỗi cụ thể | Hierarchical classification |
| Lấy giá trị chính xác | Regex tìm ứng viên, Jev chọn | Số dặm, mức lương, số người bị cắt, tên công ty | Pre-parsed value extraction |
| Chưa chắc thì nói rộng / bỏ | Đọc confidence, lùi nhãn hoặc không tính | "Có mưa" khi chưa chắc kiểu mưa; bỏ nhãn < 0,6 | Classification using confidence, Self-consistency |
| Hai ngưỡng hành động | Ưu tiên / xem xét / theo dõi | Khiếu nại nguy hiểm khi đang chạy | Guardrails for LLMs |
| Biến chữ thành cột số | Nhiều Score/Noul → bảng số để phân tích | 9 đặc điểm mỗi tiêu đề YouTube | Autoresearch feature discovery |
| Tìm khoảng trống | Gắn nhãn nhiều trục → đếm tổ hợp → tổ hợp chưa có → Jev chấm | Phong cách chưa ai vẽ | — |
| Đối chiếu và hiệu chỉnh | So với nhãn/điểm có sẵn, học lại ngưỡng | Khớp nhãn NHTSA 87%; hiệu chỉnh xác suất bàn thắng | Self-consistency (đặt ngưỡng từ dữ liệu có nhãn) |

## Ý tưởng tiếp theo (dữ liệu công khai, không cần tài khoản)

⭐ gần gũi với người Việt · 🖼️ có ảnh thật để hiện

### Việc làm và kinh tế (đang làm)
| Chủ đề | Dữ liệu | Mẫu |
|---|---|---|
| Năm 2026 công ty tuyển dev đòi gì: lương, làm từ xa, nước nào, có đòi AI không | HN "Who is hiring" (13 tháng) | Gắn nhãn hàng loạt, lấy giá trị chính xác (lương) |
| Người tìm việc mang tới gì, so với nhu cầu tuyển | HN "Who wants to be hired" | Gắn nhãn hàng loạt |
| Layoff 2026: công ty, ngành, nước, lý do, bao nhiêu người | Tiêu đề Google News | Lấy giá trị chính xác (tên, số), Choice |
| Bị layoff xong làm gì, mất bao lâu tìm việc | Bình luận HN kể chuyện | Choice, lấy giá trị chính xác (thời gian) |
| Startup mới đang tự động hóa nghề gì 🖼️ | Y Combinator 2026 (logo) | Noul + Choice |
| Công ty nào phá sản, đóng cửa, vì sao | Tiêu đề Google News | Choice, lấy giá trị chính xác (tên) |

### Đời sống
| Chủ đề | Dữ liệu | Mẫu |
|---|---|---|
| ⭐ Thành phố nào thở được nhiều ngày nhất | Open-Meteo Air Quality | Gắn nhãn hàng loạt, chưa chắc thì nói rộng |
| ⭐ Đồ ăn vặt nào "ngọt quá đà" 🖼️ | Open Food Facts | Lấy giá trị chính xác, đối chiếu |
| ⭐ Hà Nội có bao nhiêu kiểu quán cà phê | OpenStreetMap | Phân loại theo cây |
| Động đất nào đáng lo trong tuần | USGS | Hai ngưỡng hành động |

### Tin tức, Internet, tiêu dùng
| Chủ đề | Dữ liệu | Mẫu |
|---|---|---|
| ⭐ Báo Việt Nam "giật tít" đến mức nào | RSS các báo (chỉ tiêu đề, mô tả) | Chấm điểm, đối chiếu tít với mô tả |
| ⭐ Người Việt đọc gì trên Wikipedia ✅ | Lượt xem Wikipedia tiếng Việt | Phân loại theo cây, Guardrails |
| ⭐ App giao đồ ăn, ngân hàng bị chê vì gì | Đánh giá App Store Việt Nam | Chưa chắc thì bỏ, hai ngưỡng |
| Trang web có giấu lệnh cho AI không | Trang được dẫn trên Hacker News | Classifying RAG passages |
| Bình luận nào trả lời đúng câu hỏi | Ask HN | Re-ranking, Line-by-line search (đã làm với đố vui lịch sử ✅) |
| Game bị "review bom" vì đâu 🖼️ | API đánh giá Steam | Hai ngưỡng, chưa chắc thì nói rộng |
| Sách kinh điển nào mở đầu cuốn nhất | Gutendex | Biến chữ thành cột số |
| Paper có trích dẫn đúng không | arXiv | Citation check, SDE cascade |
| Hai kho sách có trùng nhau | Open Library ↔ Wikidata | Entity alignment |

### Thể thao
| Chủ đề | Dữ liệu | Mẫu |
|---|---|---|
| Euro 2024: đội nào tạo cơ hội ngon nhất | StatsBomb Open Data | Chấm điểm, hiệu chỉnh |
| Messi ở La Liga: cú sút nào khó nhất mà vẫn vào 🖼️ | StatsBomb (các mùa La Liga) | Chấm điểm, đối chiếu xG |

### Trợ lý thông minh
| Chủ đề | Dữ liệu | Mẫu |
|---|---|---|
| ⭐ AI hiểu "thứ Năm tuần sau ở Đà Lạt có mưa không" | Open-Meteo forecast + câu hỏi tự nhiên | Date extraction, Function calling, Skill suggestion |
| Văn bản mất định dạng có cứu được không | Wikisource | Structure recovery |
