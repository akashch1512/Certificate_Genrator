from Tools.image_overlay import convert_png_to_pdf
import os
png='data/generated/test_cert.png'
pdf='data/generated/test_cert.pdf'
if os.path.isfile(png):
    p=convert_png_to_pdf(png,pdf)
    print('PDF_SAVED',p)
else:
    print('PNG_MISSING')
