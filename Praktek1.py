from termcolor import cprint, colored

# data = []
# n = int(input("Masukkan jumlah mahasiswa: "))

# for i in range(n):
#     nama = input(f"Masukkan nama mahasiswa ke-{i+1}: ")
#     nilai_akhir = float(input(f"Masukkan nilai UTS {nama}: "))
#     data.append([nama, nilai_akhir])

# # data = [
# #     ["Andi", 89],
# #     ["Budi", 88],
# #     ["Caca", 90],
# #     ["Doni", 67]
# # ]

# rata_rata = []
# for nilai in data:
#     rata_rata.append(nilai[1])
# rata_rata = sum(rata_rata) / len(rata_rata)

# cprint("-" * 24, "blue")
# print(colored("| Nama".ljust(10) + "|" + "Nilai Akhir |" , "blue" ))
# cprint("-" * 24, "blue")

# for nama, nilai in data:
#     if nilai > rata_rata:
#         cprint("| "+ nama.ljust(8) + "| " + str(nilai).ljust(11)+ "|", "green")
#     else:
#         cprint("| "+ nama.ljust(8) + "| "+ str(nilai).ljust(11)+"|", "red" )
# cprint("-" * 24, "blue")

# from termcolor import cprint

pixel_char = " "
text_color = None 

for _ in range(3):  
    for _ in range(5):
        cprint(pixel_char, text_color, "on_red", end="")
    for _ in range(5):
        cprint(pixel_char, text_color, "on_green", end="")
    print()  

for _ in range(3):  
    for _ in range(5):
        cprint(pixel_char, text_color, "on_blue", end="")
    for _ in range(5):
        cprint(pixel_char, text_color, "on_yellow", end="")
    print()
# # 
# cprint("This is a colored text example.", "yellow", "on_blue", attrs=["bold"]) 