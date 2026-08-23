# def sum2num():
#     a=int(input('Enter a num:'))
#     b=int(input('Enter a num:'))
#     print(a+b)


# def area_circle():
#     r = float(input('Enter rad:'))
#     area = 3.14*r*r
#     print('Area',area)



# def diag_peri_rect():
#     l=int(input('Enter lenth:'))
#     a=int(input('Enter area:'))
#     b=a/1
#     per=2*(l+b)
#     diag=(l**2,+b**2)**(0.5)
#     print('Breadth',b,'Perimeter',p,'diagonal',diag)


# a=1
# b=2
# print("a=",a)
# print("b=",b)

# a,b=b,a
# print("After swapping")
# print("a=",a)
# print("b=",b)

# string="hello"
# Reversed_string=string[::-1]
# print("Reversedstring",Reversed_string)


# nums = [1, 2, 3, 2, 4, 5, 1]
# duplicates = []

# for i in nums:
#     if nums.count(i) > 1 and i not in duplicates:
#         duplicates.append(i)

# print("Duplicates:", duplicates)



# sentence = "Python is easy to learn"
# words = sentence.split()
# count = len(words)
# print("Number of words:", count)





# n = 10  # number of terms
# a, b = 0, 1

# print("Fibonacci series:")
# for _ in range(n):
#     print(a, end=" ")
#     a, b = b, a + b




nums = [10, 25, 3, 45, 7]

# find max
max_num = nums[0]
for i in nums:
    if i > max_num:
        max_num = i

# find min
min_num = nums[0]
for i in nums:
    if i < min_num:
        min_num = i

print("Max:", max_num)
print("Min:", min_num)
