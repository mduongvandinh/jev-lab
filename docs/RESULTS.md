# Kết quả chi tiết

Mọi con số lấy từ `episodes/<slug>/facts.json` (tạo bởi `build.py`). Giá Jev: 0,042 USD / 1 triệu token đầu vào, token đầu ra miễn phí (typesafe/jev-1.13).

## Phong cách chưa ai vẽ — `episodes/phong-cach`
- 1.031 ảnh Civitai (PG) → 178 ảnh bị loại trước khi tới Jev (nhạy cảm, người thật, meme) → 846 ảnh được gắn 6 trục.
- Bản đồ: 667 ảnh độc lập (gộp loạt ảnh gần trùng của cùng tác giả), 321 tổ hợp 4 trục đã có.
- 81 tổ hợp trống mà mọi cặp thành phần đã xuất hiện ≥ 2 lần; 13 qua vòng (mạch lạc ≥ 0,6, mới lạ ≥ 2,5/4, không giống trường phái có tên).
- Thắng: **Khối Cọ Hổ Phách** (dựng 3D × nét cọ × tông ấm × không trường phái): mạch lạc 0,81; mới lạ 3,09/4; "không giống ai" 0,53.
- Giới hạn: "chưa ai vẽ" chỉ trong mẫu; ảnh Civitai đều do AI tạo.

## Thời tiết — `episodes/thoi-tiet`
- 3.650 ngày năm 2025 × 10 thành phố; 4 câu/request (dễ chịu: Score, kiểu ngày: Choice, phơi đồ: Noul, áo mưa: Noul). 2,94 triệu token, 0,12 USD.
- Ngày đẹp (Jev chấm ≥ 2,5/4): Đà Lạt 94, Hải Phòng 86, Sa Pa 78, Hà Nội 75, Nha Trang 64, Phú Quốc 57, Huế 33, Đà Nẵng 32, Cần Thơ 22, TP.HCM 5.
- Tháng 1 đẹp nhất ở 9/10 thành phố (Sa Pa: tháng 3). Tháng 6–9 chỉ Đà Lạt còn vài ngày đẹp.
- 1.151 ngày Jev chưa chắc kiểu (confidence < 0,6) → lùi về nhãn rộng "có mưa / không mưa" bằng tổng xác suất nhãn con.
- Hỏi lại 15 lần: độ lệch chuẩn điểm dễ chịu ≈ 0,02; 3/3 ngày giữ nguyên kiểu ngày cả 15 lần.
- Giới hạn: dữ liệu tái phân tích (ERA5) ghi nhận mưa nhỏ nhiều hơn trạm đo (Hà Nội: 181 ngày ≥ 1 mm) → không dùng chỉ số "áo mưa" để kết luận.

## Xe cộ — `episodes/xe-co`
- 1.200 khiếu nại (120/dòng xe, đời 2021–2024). Lượt 1: 5 câu/request; lượt 2: lỗi cụ thể trong nhánh hệ thống. 2.383 request, 0,08 USD.
- Lỗi cụ thể nhiều nhất (chỉ tính confidence ≥ 0,6): chết máy 111, hụt ga 96, mất trợ lực lái 86, cửa/kính 51, dầu lẫn xăng 42, tự phanh vô cớ 39.
- Theo dòng xe: Civic 81% về tay lái, CR-V 51%; Kia Seltos 77% về động cơ/hộp số; Camry nổi bật ở túi khí (28%).
- Số dặm (Jev chỉ chọn trong số regex tìm được, 162 khiếu nại có số): thân xe ≈ 10k km, tay lái ≈ 15k km, động cơ ≈ 39k km, điện ≈ 50k km (trung vị).
- 65% sự cố xảy ra khi xe đang chạy. Nhãn hệ thống của Jev khớp nhãn bộ phận NHTSA 87%.
- Giới hạn: khiếu nại ở Mỹ, chưa kiểm chứng; xe bán chạy nhiều khiếu nại hơn — không phải bảng xếp hạng độ bền.

## Tiêu đề video — `episodes/tieu-de-video`
- 332 tiêu đề (37 kênh); phân tích 273 video 10–400 ngày tuổi của 35 kênh. Jev chỉ thấy tiêu đề. 0,0125 USD.
- "Nổ view" = gấp 1,5 lần trung vị lượt xem của chính kênh (23% video).
- Chênh lệch lớn nhất: tiêu đề về sản phẩm 30% vs 20% (p = 0,085); tiêu đề rất ngắn 17% vs 27% (p = 0,061). Không đặc điểm nào p < 0,05.
- Đo được rõ: mỗi kênh có "giọng" riêng (Half as Interesting: 100% tiêu đề gây tò mò; TED-Ed: 85% "giải thích vì sao").

## Bóng đá — `episodes/bong-da`
- 1.453 cú sút World Cup 2022; Jev không biết tên cầu thủ, xG hay kết quả. 1,07 triệu token, 0,045 USD.
- Không tính penalty (1.430 cú, 152 bàn): AUC Jev 0,789; xG StatsBomb 0,815. Tổng xác suất Jev 460 bàn → quá lạc quan.
- Hiệu chỉnh 10 nhóm trên 32 trận, thử trên 32 trận còn lại: Brier 0,130 → 0,080 (xG 0,077; đoán theo tỷ lệ chung 0,090); dự đoán 74 bàn, thật 70.
- Hỏi lại 15 lần: độ lệch chuẩn xác suất < 0,01.
- Kiểu cơ hội: Jev nhận đúng 46/46 cú sút phạt trực tiếp (sau khi sửa mô tả, xem LESSONS.md).

## Điện thoại — `episodes/dien-thoai`
- 3.838 bình luận Hacker News (1/2025–10/2026, phần lớn từ tháng 5/2026); 781 bình luận lạc đề do Jev tự lọc. 0,16 USD.
- Khen / chê: Pixel 27% / 34%, Samsung 24% / 41%, iPhone 23% / 39%.
- Chủ đề bị chê nhiều nhất: iPhone và Samsung — phần mềm, giao diện; Pixel — quyền riêng tư (87/134 bình luận nhắc GrapheneOS).
- ≈ 19% lời chê phần mềm iPhone nhắc tới bàn phím (đếm bằng code).
- 201 người kể đổi máy: 118 sang iPhone, 83 sang Android (truy vấn hai chiều số lượng bằng nhau).
- Giới hạn: cộng đồng lập trình viên nói tiếng Anh, không đại diện mọi người dùng.

## Tuyển dụng — `episodes/tuyen-dung`
- 3.979 tin "Who is hiring" và 6.056 hồ sơ "Who wants to be hired" (10/2025–10/2026). 8 câu/request với tin tuyển, 6 câu với hồ sơ. 12,5 triệu token, 0,53 USD.
- Người tìm việc trên 100 tin tuyển: 104 (10/2025) → 242 (8/2026) → 218 (9/2026). Không tính 10/2026 (mới đăng vài ngày).
- Làm từ xa: 88% hồ sơ muốn từ xa; tin cho từ xa hẳn 46%, hybrid 24%, chỉ tại chỗ 23% (nhãn chắc từ 0,6).
- Lương (864 tin ghi bằng $, Jev chỉ chọn trong số tiền regex tìm được; điểm giữa khoảng): quản lý kỹ thuật 195k, DevOps 192k, ML/AI 190k, backend và full-stack 175k. Có ca Jev chọn sai (một tin có cả $500k và $250k, Jev chọn $250k cho cả hai đầu).
- AI: 31% tin đòi kinh nghiệm AI, 48% hồ sơ ghi có AI, 44% công ty làm sản phẩm lõi AI. Lương trung vị tin đòi AI 185k vs không đòi 182,5k.
- Tin cho người mới đi làm 1,3% (50 tin), hồ sơ người mới 6,6%. Bảo lãnh visa 3%. 60% tin ở Mỹ.

## Layoff — `episodes/layoff`
- 2.491 tiêu đề Google News (1–10/2026); 1.871 là tin một công ty cụ thể cắt việc. 515 bình luận HN, 283 người tự kể. 0,14 USD.
- Bị nhắc nhiều nhất (số tiêu đề, không phải số người): Meta 148, Amazon 126, Oracle 89, Disney 61, Nike 59.
- Ngành: phần mềm/Internet 417, bán lẻ 295, truyền thông/giải trí 261, nhà nước/giáo dục 180.
- Lý do (556 tin có nêu): AI 179 (32%), tái cấu trúc 166, cắt chi phí 69, bán chậm 59. Nêu AI nhiều nhất: Meta, Oracle, Block.
- Sau layoff (113 người nói rõ): vẫn đang tìm 35 (tâm trạng 1,3/4), việc mới cùng nghề 26 (2,4), tự mở công ty 18 (2,6), việc khác nghề 15 (2,1).
- Giới hạn: RSS trả tối đa khoảng 100 tin mỗi truy vấn nên không so xu hướng theo tháng; số người trong tiêu đề hay là tổng cả ngành nên không xếp hạng theo số người.

## Công ty mới và đóng cửa — `episodes/cong-ty`
- 678 startup YC (W26, P26, S26, F26): 83% lõi AI; 458 (68%) nhắm tự động hóa việc con người đang làm.
- Mảng: AI agent/tự động hóa 144, công cụ lập trình 97, tài chính 77, phần mềm ngành 71, robot 62.
- Việc bị nhắm: phân tích dữ liệu 60, lập trình/kiểm thử 56, lao động chân tay 39, hành chính y tế 23, bán hàng 22, kế toán 21, pháp lý 17.
- 72% đặt ở San Francisco; đội trung vị 2 người.
- 2.330 tiêu đề đóng cửa → 1.269 về một công ty cụ thể. Ngành: bán lẻ 313, vận tải/du lịch 194. Lý do có nêu: nợ/cạn tiền 105, gian lận/kiện tụng 58.
- Bị nhắc nhiều: Spirit Airlines, Saks Global, Eddie Bauer, West Marine. 0,14 USD.

## Ronaldo — `episodes/ronaldo`
- Không dùng Jev: cộng từ bảng thống kê Wikipedia (bản 4/10/2026). CLB 1.106 trận/833 bàn; Bồ Đào Nha 234/146; đỉnh 61 bàn mùa 2014–15; 35 danh hiệu tập thể.

## Nguồn dữ liệu và giấy phép

| Nguồn | Dùng trong | Ghi chú |
|---|---|---|
| Open-Meteo Historical API | thoi-tiet | CC BY 4.0, ghi nguồn |
| NHTSA Complaints API | xe-co | Dữ liệu công của chính phủ Mỹ |
| YouTube RSS | tieu-de-video | Tiêu đề, ảnh thuộc các kênh; không lưu trong repo |
| StatsBomb Open Data | bong-da | Miễn phí, ghi nguồn StatsBomb |
| Hacker News (API Algolia) | dien-thoai, tuyen-dung, layoff | Bình luận thuộc người viết; không lưu trong repo |
| Civitai API | phong-cach | Ảnh thuộc tác giả; không lưu trong repo |
| Google News RSS | layoff, cong-ty | Chỉ tiêu đề; không lưu trong repo |
| Y Combinator API | cong-ty | Thông tin công khai của công ty |
| Wikimedia Commons | bong-da, ronaldo (ảnh) | CC BY / CC BY-SA, ghi tác giả trên video |
| Wikipedia | ronaldo | CC BY-SA; bảng thống kê tải lại bằng collect.py |
