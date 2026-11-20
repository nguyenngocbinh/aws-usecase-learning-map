# Lab safety, security and cost

## Safety baseline

1. Chỉ dùng AWS account dành cho học tập, không dùng tài khoản hoặc mạng production.
2. Chỉ dùng synthetic/anonymized datasets; không tải dữ liệu ngân hàng, PII, credentials hoặc secrets lên repo/AWS lab.
3. Bật MFA và dùng least-privilege IAM.
4. Với CI/CD, ưu tiên OIDC federation và temporary role sessions.
5. Không public S3 bucket để thuận tiện cho lab; dùng presigned URL hoặc quyền truy cập có kiểm soát nếu cần.
6. Không commit file `.env`, access keys, Terraform state hoặc database dumps.

## Cost checklist for every lab

- Region và ngày kiểm tra giá.
- Tài nguyên được tạo và pricing dimension (hour, request, GB-month, data transfer, capacity).
- Thời lượng lab ước tính và giả định tải.
- Các thành phần có thể tiếp tục tính phí sau khi hoàn tất.
- Lệnh/console cleanup và bước xác minh không còn tài nguyên.
- Kiểm tra Cost Explorer/Billing sau lab.

> Pricing thay đổi theo Region, usage, network transfer, storage class, discounts và thuế. Không dùng con số ước lượng cũ làm cam kết giá.

## Cleanup pattern

Mỗi lab phải có phần teardown cụ thể. Với Terraform, kiểm tra workspace/account/region trước khi chạy `terraform destroy`. Không chạy lệnh destroy khi chưa xác nhận đúng learning environment.

## Data governance

Dữ liệu mẫu phải synthetic, có data dictionary, retention rule và license rõ ràng. Hình ảnh, biểu tượng và sơ đồ bên ngoài phải ghi nguồn, quyền sử dụng và điều kiện attribution.
