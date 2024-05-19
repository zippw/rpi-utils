import time

step = 10


# Gradient generator
def stepped(c1, c2, i):
    return round(c1 + ((c2 - c1) / step * i))


colors = [
    [255, 113, 206],
    [185, 103, 255],
    [1, 205, 254],
    [5, 255, 161],
    [255, 251, 250],
    [255, 113, 206],
]
gradient = []
for i in range(len(colors)):
    gradient.append(colors[i])
    n = (i + 1) % len(colors)
    for j in range(1, step):
        gradient.append(
            [
                stepped(colors[i][0], colors[n][0], j),
                stepped(colors[i][1], colors[n][1], j),
                stepped(colors[i][2], colors[n][2], j),
            ]
        )

lenta = gradient[slice(0, 7)]


def gen_gradient(gradient, c):
    str = "\x1B[0;0H\x1B[0J"
    for i in range(len(lenta)):
        r, g, b = gradient[(c + i) % len(gradient)]
        str += "\x1B[48;2;{};{};{}m  \x1B[0m".format(int(r), int(g), int(b))
    print(str)
    c = (c + 1) % len(gradient)
    return c


c = 0
while True:
    c = gen_gradient(gradient, c)
    time.sleep(0.05)
