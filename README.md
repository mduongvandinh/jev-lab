# Jev Lab

**Thí nghiệm thật với Jev trên dữ liệu công khai**: thời tiết, khiếu nại xe, tiêu đề YouTube, cú sút World Cup, bình luận về điện thoại, ảnh AI…
Mỗi thí nghiệm là một quy trình chạy lại được từ đầu đến cuối: thu dữ liệu → Jev trả lời câu hỏi có kiểu cho từng mục → thống kê → kết luận, kèm chi phí thật và giới hạn của dữ liệu. Mỗi thí nghiệm còn xuất ra một video dọc (Reels) bằng Remotion.

*Real experiments with [Jev](https://github.com/wuyoscar/jev-skill) (TypeSafe's typed decision model: Noul, Choice, Score) on public data. Each experiment is a reproducible pipeline — collect → ask Jev typed questions per item → aggregate → conclude, with real cost and caveats — plus an optional vertical video. Docs are in Vietnamese.*

## Kết quả

| Thí nghiệm | Dữ liệu | Phát hiện chính | Kỹ thuật (cookbook TypeSafe) | Chi phí Jev |
|---|---|---|---|---|
| [Phong cách chưa ai vẽ](episodes/phong-cach) | 1.031 ảnh Civitai | Tìm ra "Khối Cọ Hổ Phách" trong 81 tổ hợp còn trống, 13 qua vòng | Choice nhiều trục, Noul + Score chấm ứng viên | ≈ 0,10 USD |
| [Thời tiết](episodes/thoi-tiet) | 3.650 ngày, 10 thành phố Việt Nam (Open-Meteo) | Đà Lạt 94 ngày đẹp, TP.HCM 5; tháng 1 đẹp nhất ở 9/10 nơi | Parallel questions, Classification using confidence, Self-consistency | 0,12 USD |
| [Xe cộ](episodes/xe-co) | 1.200 khiếu nại NHTSA, 10 dòng xe | Chết máy đứng đầu; 81% khiếu nại về Civic là tay lái; nhãn Jev khớp nhãn NHTSA 87% | Hierarchical classification, Pre-parsed value extraction, hai ngưỡng kiểu Guardrails | 0,08 USD |
| [Tiêu đề video](episodes/tieu-de-video) | 332 tiêu đề, 37 kênh YouTube | Không có công thức tiêu đề: mọi chênh lệch trong mức may rủi (kiểm định hoán vị) | Autoresearch feature discovery | 0,01 USD |
| [Bóng đá](episodes/bong-da) | 1.453 cú sút World Cup 2022 (StatsBomb) | Chỉ đọc mô tả, Jev xếp hạng cơ hội gần bằng xG (AUC 0,79 vs 0,815) nhưng quá lạc quan; hiệu chỉnh xong sai số ≈ xG | Parallel questions, Self-consistency, hiệu chỉnh từ dữ liệu có nhãn | 0,05 USD |
| [Điện thoại](episodes/dien-thoai) | 3.838 bình luận Hacker News | Pixel được khen nhiều nhất (27%); iPhone bị chê vì phần mềm; 118 người sang iPhone, 83 sang Android | Parallel questions, Self-consistency: choices (ngưỡng 0,6) | 0,16 USD |
| [Tuyển dụng](episodes/tuyen-dung) | 10.035 tin tuyển dụng và hồ sơ tìm việc (HN, 13 tháng) | Người tìm việc trên 100 tin tăng từ 104 lên 218; 95% muốn làm từ xa, chỉ 46% tin cho phép; biết AI gần như không thêm lương | Parallel questions, Pre-parsed value extraction (lương) | 0,53 USD |
| [Layoff](episodes/layoff) | 2.491 tiêu đề tin + 515 chuyện kể (Google News, HN) | AI là lý do được nêu nhiều nhất (32% tin có lý do); người tự mở công ty sau layoff vui nhất, người còn tìm việc tệ nhất | Pre-parsed value extraction (tên công ty), Choice | 0,14 USD |
| [Công ty mới & đóng cửa](episodes/cong-ty) | 678 startup YC 2026 + 2.330 tiêu đề đóng cửa | 83% startup lấy AI làm lõi, 68% nhắm tự động hóa việc của người (nhiều nhất: phân tích dữ liệu, lập trình); đóng cửa nhiều nhất ở bán lẻ | Parallel questions, Pre-parsed value extraction | 0,14 USD |
| [Wikipedia đọc gì](episodes/wiki-doc-gi) | 1.500 bài vi.wikipedia đọc nhiều nhất, 103 triệu lượt xem | 38% lượt đọc là về con người; 56% là chủ đề Việt Nam; trạm chắn hai ngưỡng chặn 46 bài, 14 bài vào diện xem xét | Hierarchical classification, Guardrails, Parallel questions | 0,12 USD |
| [Vua Việt Nam](episodes/vua-viet-nam) | 99 vua (939–1945) trên vi.wikipedia | Cứ khoảng 8 vị thì 1 vị bị giết; trị vì trung vị 8 năm; năm sinh, năm mất Jev chọn khớp 74/74 với nguồn | Date extraction, Pre-parsed value extraction | < 0,01 USD |
| [Đố vui lịch sử](episodes/do-vui) | 24 câu đố, 5.095 đoạn văn | Từ khóa đúng 15/20, thêm Jev xếp lại 19/20; nhận ra 4/4 câu bẫy | Re-ranking, Line-by-line search | < 0,01 USD |
| [Ronaldo](episodes/ronaldo) | Bảng thống kê Wikipedia | Hồ sơ số liệu (không dùng Jev): 1.340 trận, 979 bàn, 35 danh hiệu | — | 0 |

Chi tiết từng con số: [docs/RESULTS.md](docs/RESULTS.md) · Các mẫu áp dụng Jev và hơn 30 ý tưởng: [docs/USE_CASES.md](docs/USE_CASES.md) · Bài học và lỗi đã gặp: [docs/LESSONS.md](docs/LESSONS.md)

## Cấu trúc

```
lab/                 engine dùng chung
  config.py          đọc cấu hình từ biến môi trường hoặc lab/local.json (không đưa lên git)
  jevcall.py         gọi Jev qua CLI của repo jev-skill (provider TypeSafe); key chỉ truyền cho tiến trình con
  common.py          ask_all: mỗi mục một request, chạy tiếp được khi gián đoạn; cost: tính tiền từ token thật
  pick.py            Pre-parsed value extraction: regex tìm ứng viên (tiền, số lượng, tên, thời gian), Jev chỉ chọn
  narrate.py         lồng tiếng tiếng Việt (VieNeu), phụ đề theo câu — tùy chọn
  publish.py, stills.sh
episodes/<slug>/     collect.py → ask.py → build.py → episode.json + facts.json; narration.json (lời đọc)
viz/                 Remotion: 10 kiểu cảnh dùng chung (intro, scan, technique, label, heat, bars, repeat, judge, pitch, reveal)
docs/                kết quả, use case, bài học
```

## Chạy lại một thí nghiệm

Cần Python 3.10+ (không cần thư viện ngoài cho phần dữ liệu và Jev), repo [jev-skill](https://github.com/wuyoscar/jev-skill) và một key TypeSafe.

```bash
export JEV_CLI=/path/to/jev-skill/skills/jev/scripts/jev.py
export TYPESAFE_API_KEY=...            # hoặc JEV_ENV_FILE=/path/to/.env
cd episodes/thoi-tiet
python3 collect.py                     # tải dữ liệu công khai vào data/
python3 ask.py                         # gọi Jev, ghi jev/answers.jsonl (chạy lại sẽ tiếp tục chỗ dừng)
python3 build.py                       # in facts.json: mọi con số của kết luận
```

Làm video (tùy chọn): `cd viz && npm install`, viết `narration.json`, rồi `python lab/narrate.py <slug> && python3 lab/publish.py && cd viz && npx remotion render src/index.ts Lab-<slug> out.mp4`.
Remotion có [điều khoản giấy phép riêng](https://www.remotion.dev/license) cho công ty.

## Nguyên tắc

- **Chỉ dữ liệu công khai.** Nguồn chặn truy cập tự động hoặc tác giả gắn cờ cấm AI thì dừng, không lách (DeviantArt là ví dụ).
- **Jev phán đoán, code tính toán.** Đếm, regex, so số để code làm; Jev trả lời câu cần hiểu nghĩa, kèm xác suất.
- **Mọi con số lấy từ `facts.json`**, ghi cỡ mẫu, giới hạn dữ liệu, và nói thẳng khi không có tín hiệu.
- Repo không chứa dữ liệu thô, ảnh hay video của bên thứ ba; `collect.py` tải lại từ nguồn. Xem giấy phép từng nguồn trong [docs/RESULTS.md](docs/RESULTS.md).

## Giấy phép

Code: MIT (xem [LICENSE](LICENSE)). Dữ liệu thuộc về nguồn gốc của nó.
