from PIL import Image, ImageTk

img = Image.open("Resources/pill_icon.png")
img.show()
img2 = img.copy()
img2.thumbnail((40,40))
img2.show()
print(type(img2))
