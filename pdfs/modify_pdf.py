
# from pdfrw import PdfReader, PdfWriter, PageMerge

# def merge_pdf_vertically_with_margins(input_path, output_path, margin=20):
#     """
#     Merge two PDF pages vertically on A4 with margins
#     :param input_path: Input PDF path
#     :param output_path: Output PDF path
#     :param margin: Margin size in points (default 20)
#     """
#     reader = PdfReader(input_path)
#     writer = PdfWriter()
    
#     # A4 dimensions in points (595 x 842)
#     a4_width = 595
#     a4_height = 842
    
#     # Calculate available space after margins
#     usable_width = a4_width - 2 * margin
#     usable_height_per_page = (a4_height - 3 * margin) / 2  # 3 margins (top, between, bottom)
    
#     for i in range(0, len(reader.pages), 2):
#         # Create new A4 page
#         blank = PageMerge()
#         blank.mbox = [0, 0, a4_width, a4_height]
        
#         # Process first page (top)
#         if i < len(reader.pages):
#             page = reader.pages[i]
#             orig_width = float(page.MediaBox[2])
#             orig_height = float(page.MediaBox[3])
            
#             # Calculate scale to fit within margins
#             width_scale = usable_width / orig_width
#             height_scale = usable_height_per_page / orig_height
#             scale = min(width_scale, height_scale)
            
#             # Calculate centered position
#             scaled_width = orig_width * scale
#             scaled_height = orig_height * scale
#             x_pos = margin + (usable_width - scaled_width) / 2
#             y_pos = a4_height - margin - scaled_height - (usable_height_per_page - scaled_height)/2
            
#             # Add to page
#             top = PageMerge().add(page)[0]
#             top.x = x_pos
#             top.y = y_pos
#             top.scale(scale)
#             blank.add(top)
        
#         # Process second page (bottom)
#         if i+1 < len(reader.pages):
#             page = reader.pages[i+1]
#             orig_width = float(page.MediaBox[2])
#             orig_height = float(page.MediaBox[3])
            
#             # Use same scale as top page for consistency
#             scaled_width = orig_width * scale
#             scaled_height = orig_height * scale
#             x_pos = margin + (usable_width - scaled_width) / 2
#             y_pos = margin + (usable_height_per_page - scaled_height)/2
            
#             # Add to page
#             bottom = PageMerge().add(page)[0]
#             bottom.x = x_pos
#             bottom.y = y_pos
#             bottom.scale(scale)
#             blank.add(bottom)
        
#         writer.addpage(blank.render())
    
#     writer.write(output_path)
#     print(f"Created {output_path} with 2 pages per A4 sheet with {margin}pt margins")

# # Example usage:
# merge_pdf_vertically_with_margins("input_pdfs/L1 AND L2.pdf", "output_pdfs/output_vertical_a43.pdf", margin=60)
# print(f"Successfully created  with 2 pages merged per sheet")



# from pdfrw import PdfReader, PdfWriter, PageMerge
# import os
# from pathlib import Path

# def merge_pdf_vertically_with_margins(input_path, output_path, margin=60):
#     """
#     Merge two PDF pages vertically on A4 with margins
#     :param input_path: Input PDF path
#     :param output_path: Output PDF path
#     :param margin: Margin size in points
#     """
#     reader = PdfReader(input_path)
#     writer = PdfWriter()
    
#     # A4 dimensions in points (595 x 842)
#     a4_width = 595
#     a4_height = 842
    
#     # Calculate available space after margins
#     usable_width = a4_width - 2 * margin
#     usable_height_per_page = (a4_height - 3 * margin) / 2
    
#     for i in range(0, len(reader.pages), 2):
#         blank = PageMerge()
#         blank.mbox = [0, 0, a4_width, a4_height]
        
#         # Process first page (top)
#         if i < len(reader.pages):
#             page = reader.pages[i]
#             orig_width = float(page.MediaBox[2])
#             orig_height = float(page.MediaBox[3])
            
#             width_scale = usable_width / orig_width
#             height_scale = usable_height_per_page / orig_height
#             scale = min(width_scale, height_scale)
            
#             scaled_width = orig_width * scale
#             scaled_height = orig_height * scale
#             x_pos = margin + (usable_width - scaled_width) / 2
#             y_pos = a4_height - margin - scaled_height - (usable_height_per_page - scaled_height)/2
            
#             top = PageMerge().add(page)[0]
#             top.x = x_pos
#             top.y = y_pos
#             top.scale(scale)
#             blank.add(top)
        
#         # Process second page (bottom)
#         if i+1 < len(reader.pages):
#             page = reader.pages[i+1]
#             orig_width = float(page.MediaBox[2])
#             orig_height = float(page.MediaBox[3])
            
#             scaled_width = orig_width * scale
#             scaled_height = orig_height * scale
#             x_pos = margin + (usable_width - scaled_width) / 2
#             y_pos = margin + (usable_height_per_page - scaled_height)/2
            
#             bottom = PageMerge().add(page)[0]
#             bottom.x = x_pos
#             bottom.y = y_pos
#             bottom.scale(scale)
#             blank.add(bottom)
        
#         writer.addpage(blank.render())
    
#     writer.write(output_path)

# def process_pdf_folder(input_folder, output_folder, margin=60):
#     """
#     Process all PDFs in input folder and save merged versions to output folder
#     """
#     # Create output folder if it doesn't exist
#     Path(output_folder).mkdir(parents=True, exist_ok=True)
    
#     # Process each PDF in input folder
#     for filename in os.listdir(input_folder):
#         if filename.lower().endswith('.pdf'):
#             input_path = os.path.join(input_folder, filename)
#             output_filename = f"{os.path.splitext(filename)[0]}_merged.pdf"
#             output_path = os.path.join(output_folder, output_filename)
            
#             print(f"Processing: {filename}")
#             try:
#                 merge_pdf_vertically_with_margins(input_path, output_path, margin)
#                 print(f"Created: {output_filename}")
#             except Exception as e:
#                 print(f"Error processing {filename}: {str(e)}")
    
#     print("\nAll PDFs processed successfully!")

# # Example usage:
# input_folder = "input_pdfs"  # Folder containing your original PDFs
# output_folder = "output_pdfs"  # Folder where merged PDFs will be saved
# margin_size = 60  # Adjust margin size as needed

# process_pdf_folder(input_folder, output_folder, margin_size)


from pdfrw import PdfReader, PdfWriter, PageMerge
import os
from pathlib import Path

def merge_pdf_vertically_with_margins(input_path, output_path, margin=60):
    """
    Merge two PDF pages vertically on A4 with margins
    :param input_path: Input PDF path
    :param output_path: Output PDF path
    :param margin: Margin size in points
    """
    reader = PdfReader(input_path)
    writer = PdfWriter()
    
    # A4 dimensions in points (595 x 842)
    a4_width = 595
    a4_height = 842
    
    # Calculate available space after margins
    usable_width = a4_width - 2 * margin
    usable_height_per_page = (a4_height - 3 * margin) / 2
    
    for i in range(0, len(reader.pages), 2):
        blank = PageMerge()
        blank.mbox = [0, 0, a4_width, a4_height]
        
        # Process first page (top)
        if i < len(reader.pages):
            page = reader.pages[i]
            orig_width = float(page.MediaBox[2])
            orig_height = float(page.MediaBox[3])
            
            width_scale = usable_width / orig_width
            height_scale = usable_height_per_page / orig_height
            scale = min(width_scale, height_scale)
            
            scaled_width = orig_width * scale
            scaled_height = orig_height * scale
            x_pos = margin + (usable_width - scaled_width) / 2
            y_pos = a4_height - margin - scaled_height - (usable_height_per_page - scaled_height)/2
            
            top = PageMerge().add(page)[0]
            top.x = x_pos
            top.y = y_pos
            top.scale(scale)
            blank.add(top)
        
        # Process second page (bottom)
        if i+1 < len(reader.pages):
            page = reader.pages[i+1]
            orig_width = float(page.MediaBox[2])
            orig_height = float(page.MediaBox[3])
            
            scaled_width = orig_width * scale
            scaled_height = orig_height * scale
            x_pos = margin + (usable_width - scaled_width) / 2
            y_pos = margin + (usable_height_per_page - scaled_height)/2
            
            bottom = PageMerge().add(page)[0]
            bottom.x = x_pos
            bottom.y = y_pos
            bottom.scale(scale)
            blank.add(bottom)
        
        writer.addpage(blank.render())
    
    writer.write(output_path)

def process_pdf_folder(input_folder, margin=60):
    """
    Process all PDFs in input folder and save merged versions to automatically created output folder
    :param input_folder: Path to folder containing PDFs to process
    :param margin: Margin size in points
    :return: Path to the created output folder
    """
    # Create output folder name
    input_folder_name = os.path.basename(os.path.normpath(input_folder))
    output_folder = f"{input_folder_name}_merged_out"
    
    # Create full output path (in same directory as input folder)
    output_path = os.path.join(os.path.dirname(input_folder), output_folder)
    
    # Create output folder if it doesn't exist
    Path(output_path).mkdir(parents=True, exist_ok=True)
    
    # Process each PDF in input folder
    processed_files = 0
    for filename in os.listdir(input_folder):
        if filename.lower().endswith('.pdf'):
            input_file = os.path.join(input_folder, filename)
            output_file = os.path.join(output_path, f"{os.path.splitext(filename)[0]}_merged.pdf")
            
            print(f"Processing: {filename}")
            try:
                merge_pdf_vertically_with_margins(input_file, output_file, margin)
                processed_files += 1
                print(f"Created: {os.path.basename(output_file)}")
            except Exception as e:
                print(f"Error processing {filename}: {str(e)}")
    
    print(f"\nProcessing complete! {processed_files} PDFs created in: {output_path}")
    return output_path

# Example usage:
input_folder = "pdfs/input_pdf1"  # Replace with your folder path
margin_size = 60  # Adjust margin size as needed

output_folder = process_pdf_folder(input_folder, margin_size)