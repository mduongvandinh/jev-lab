# Phong cách chưa ai vẽ (style gap)

Thí nghiệm đầu tiên của Jev Lab: tìm một phong cách hình ảnh chưa xuất hiện trong 1.031 ảnh công khai trên Civitai.

1. `collect_civitai.py` — tải ảnh PG qua API công khai (giãn cách 3 giây, chờ khi quá tải), đo bảng màu (`collect.py: palette`, cần ffmpeg).
   DeviantArt đã được thử trước nhưng chặn truy cập tự động (403) và nhiều tác phẩm gắn cờ cấm AI, nên đã dừng, không lách.
2. `make_sheets.py` — ghép ảnh thành tấm 4×4 đánh số. Jev chỉ đọc chữ, nên một agent đọc ảnh mô tả từng tấm thành
   `descriptions/sheet_NNN.json` ({id, description, exclude, exclude_reason}); ảnh nhạy cảm, người thật, meme bị loại (178 ảnh).
3. `classify.py` — Jev gắn 6 trục (chất liệu, kỹ thuật, bảng màu, chủ đề, cảm xúc, trường phái) cho 846 ảnh, 6 câu Choice/request.
4. `gap.py` — tổ hợp 4 trục có 0 ảnh nhưng mọi cặp thành phần đã xuất hiện ≥ 2 lần; Jev chấm 81 ứng viên
   (mạch lạc: Noul, mới lạ: Score, giống trường phái nào: Choice, hợp mạng xã hội: Score). 13 qua vòng.
5. `export_viz.py`, `narrate.py`, `viz-src/` — video mô phỏng (Remotion).

Kết quả: **Khối Cọ Hổ Phách** — xem `out/style-guide.md`, `out/prompts.txt`, `out/style.json`. Chi phí Jev ≈ 0,10 USD.
"Chưa ai vẽ" chỉ đúng trong phạm vi 846 ảnh đã phân tích; ngoài đời có họ hàng gần là hoạt hình 3D vẽ tay (NPR).
