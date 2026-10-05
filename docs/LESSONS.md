# Bài học khi dùng Jev trên dữ liệu thật

## Cách hỏi
1. **Gộp mọi câu của một mục vào một request** (cookbook Parallel questions). 3–9 câu/request là bình thường; mỗi request 700–1.500 token đầu vào.
2. **Jev chỉ đọc chữ.** Ảnh phải được mô tả thành chữ trước (một agent đọc ảnh ghép 4×4), hoặc đổi thành số đo (tọa độ, khoảng cách, góc).
3. **Việc code làm được thì để code làm**: đếm, regex, so số, độ dài tiêu đề. Jev dành cho câu cần hiểu nghĩa.
4. **Giá trị chính xác: regex tìm, Jev chỉ chọn** (cookbook Pre-parsed value extraction). Viết regex tìm dư hơn sót. Tiêu đề tiếng Anh viết hoa mọi chữ → lấy mọi cụm con 1–3 chữ làm ứng viên tên công ty, nếu không Jev sẽ chọn "none".
5. **Tên trường trong `state` là một phần của câu hỏi.** Trường `build_up: "From Free Kick"` khiến Jev xếp 145 cú sút trong pha bóng sống thành "đá phạt trực tiếp". Đổi thành `attack_started_from: "a free kick earlier in the move"` → khớp đúng 46/46. Luôn đối chiếu với nhãn có sẵn khi có.
6. **Giấu thứ dễ gây thiên vị**: tên cầu thủ, tên kênh, kết quả, lượt xem.

## Đọc kết quả
7. **CLI `jev.py decide` trả exit 2 khi có quyết định dưới ngưỡng — vẫn có đủ kết quả ở stdout**, không phải lỗi. Coi exit 2 là lỗi từng làm phí khoảng 300 request.
8. **Xác suất tốt để xếp hạng chưa chắc tốt làm con số.** Bóng đá: AUC gần mô hình chuyên dụng nhưng tổng dự đoán gấp 3 thực tế. Hiệu chỉnh trên một nửa dữ liệu có nhãn, kiểm tra trên nửa còn lại.
9. **Chưa chắc thì nói rộng**: nhãn rộng = tổng xác suất các nhãn con, không tốn thêm request (thời tiết: "có mưa" = mưa phùn + mưa + mưa lớn).
10. **Ngưỡng 0,6 để tính hay bỏ** (Self-consistency: choices) và **hai ngưỡng hành động** (Guardrails) đặt trong code, đổi được bất cứ lúc nào.
11. **Hỏi lại cùng câu 15 lần**: độ lệch chuẩn quan sát được 0,006–0,03 — Jev sai thì sai nhất quán, nên hiệu chỉnh được.

## Dữ liệu và trung thực
12. **Soát dữ liệu bất thường trước khi kết luận**: ERA5 ghi nhiều ngày mưa nhỏ → bỏ chỉ số "áo mưa".
13. **Không có tín hiệu thì nói thẳng**, kèm kiểm định hoán vị (tiêu đề video).
14. **Thiết kế truy vấn để không lệch mẫu**: bỏ truy vấn "grapheneos pixel"; tìm hai chiều đổi máy với số truy vấn bằng nhau; nêu rõ số khiếu nại phụ thuộc doanh số.
15. **Tôn trọng nguồn**: dừng khi bị chặn (DeviantArt 403), tôn trọng cờ noai, loại ảnh nhạy cảm/người thật trước khi gửi đi, ghi công tác giả, không hiện mục bị loại.

## Làm việc với Wikipedia và Wikimedia
18. **User-Agent phải có thông tin liên hệ** (link repo) theo chính sách Wikimedia, nếu không dễ bị 429. Gom 20 bài mỗi request (`prop=extracts|pageimages&exintro`) thay vì 1 request/bài: 1.500 bài từ 1.500 xuống 75 request.
19. **Dừng tiến trình cũ trước khi chạy lại**: một bộ thu bị treo vẫn ghi đè cùng file; `pkill` theo tên lệnh không bắt được vì tiến trình hiện đường dẫn Python đầy đủ — kiểm tra bằng `lsof`.
20. **Ngưỡng hiển thị chặt hơn ngưỡng thống kê**: bài y học hay sinh học không bị coi là người lớn (đúng), nhưng không nên lên Reels. Dùng vùng "xem xét" của Guardrails để ẩn khỏi video mà vẫn tính vào số liệu.
21. **Chỉ dùng ảnh trên Wikimedia Commons** (đường dẫn `/wikipedia/commons/`), lấy tác giả + giấy phép bằng `imageinfo&iiprop=extmetadata` (50 file/request).

## Video
16. Bộ tách câu cho TTS chỉ được tách khi dấu câu đứng trước khoảng trắng — nếu không "3.650", "TP.HCM", "jev-1.12" bị cắt đôi.
17. Phụ đề dài quá 3 dòng sẽ che nội dung: viết câu ngắn.
22. Lời đọc và hình phải dùng cùng một mẫu số (ví dụ "95% trong số hồ sơ có nhãn chắc chắn" chứ không phải 88% trên mọi hồ sơ).
