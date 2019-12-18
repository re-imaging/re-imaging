import matplotlib.pyplot as plt
import numpy as np
import sys

# utility script for plotting the error rate from keras text output

filename = sys.argv[1]

a = np.array([0.0])
b = np.array([0.0])

count = 0

with open(filename) as f:
    content = f.readlines()
    for line in content:
        # nums = [(float(line.split(" ")[7]), (float(line.split(" ")[9])]
        nums = line.split()
        n = []
        if len(nums) == 13 and count < 100:
            count += 1
            print(nums)
            # print("list correct length!")
            # n.append(nums[10])
            # n.append(nums[12])
            # test = 0.0
            # test = nums(10)
            # print(test)
            print("n[1]---> " + str(nums[10]))
            # print("n[0]---> " + str(nums[12]))

            a = np.append(a, [nums[10]])
            b = np.append(b, [nums[12]])
            # a = np.append(a, [1, 2])

print(a)
print(b)

plt.plot(a)
plt.plot(b)
plt.show()

        # n[1] = nums[27]
        # print(line)
        # print(len(nums))

# f = open(filename)
# lines = f.read()
#
# for line in lines:
#     print(line)
