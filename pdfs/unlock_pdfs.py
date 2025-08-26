import pikepdf
import os

# CHANGE these paths
input_folder = r"C:\locked"
output_folder = r"C:\unlocked"
password = "xxx"   

os.makedirs(output_folder, exist_ok=True)

for file in os.listdir(input_folder):
    if file.lower().endswith(".pdf"):
        input_path = os.path.join(input_folder, file)
        output_path = os.path.join(output_folder, file)

        try:
            with pikepdf.open(input_path, password=password) as pdf:
                pdf.save(output_path)
            print(f"✅ Unlocked: {file}")
        except Exception as e:
            print(f"❌ Failed: {file} ({e})")

print("🎉 All PDFs processed!")
