import math
import itertools

# ----------------------------
# Distance from a point to a hyperrectangle
# ----------------------------
def rect_distance(rect, point):
    dist_sq = 0.0
    D = len(point)
    for j in range(D):
        low, high = rect[j]
        pj = point[j]
        if pj < low:
            dist_sq += (low - pj) ** 2
        elif pj > high:
            dist_sq += (pj - high) ** 2
    return math.sqrt(dist_sq)

# ----------------------------
# Extend a rectangle to include a point
# ----------------------------
def extend(rect, point):
    D = len(point)
    for j in range(D):
        rect[j][0] = min(rect[j][0], point[j])
        rect[j][1] = max(rect[j][1], point[j])

# ----------------------------
# Load and split dataset (with label balance)
# ----------------------------
with open("random_dataset.csv", "r") as f:
    data = []
    for line in f:
        parts = line.strip().split(",")
        if len(parts) < 2:
            continue
        try:
            nums = list(map(float, parts))
            data.append(nums)
        except:
            continue

# Number of training and test samples
n_train = int(input("Enter Train:"))
n_test = int(input("Enter Test:"))

if len(data) < n_train + n_test:
    raise ValueError(f"Need at least {n_train + n_test} rows, but got {len(data)}")

train_data = data[:n_train]
test_data  = data[n_train : n_train + n_test]

# ----------------------------
# Training
# ----------------------------
model = []

for sample in train_data:
    point = sample[:-1]
    label = sample[-1]
    D = len(point)

    placed = False

    # A) Try to place into an existing rectangle
    for i in range(len(model)):
        rect = model[i]
        rect_label = rect[-1]

        if all(rect[j][0] <= point[j] <= rect[j][1] for j in range(D)):
            if rect_label == label:
                placed = True
                break
            else:
                mids = [(rect[j][0] + rect[j][1]) / 2.0 for j in range(D)]
                bit_pattern = tuple(0 if point[j] <= mids[j] else 1 for j in range(D))
                children = []

                for bits in itertools.product([0, 1], repeat=D):
                    child_box = []
                    for j in range(D):
                        if bits[j] == 0:
                            child_box.append([rect[j][0], mids[j]])
                        else:
                            child_box.append([mids[j], rect[j][1]])
                    if bits == bit_pattern:
                        children.append(child_box + [label])
                    else:
                        children.append(child_box + [rect_label])

                model.pop(i)
                model.extend(children)
                placed = True
                print("SPLIT")
                break

    if placed:
        continue

    # B) Try to extend nearest same-label rectangle
    nearest = None
    min_dist = float("inf")
    for r in model:
        if r[-1] == label:
            d = rect_distance(r, point)
            if d < min_dist:
                min_dist = d
                nearest = r

    if nearest:
        extend(nearest[:D], point)
        print("EXTEND")
    else:
        # C) Create new rectangle
        model.append([[v, v] for v in point] + [label])

print(f"Training completed. Total rectangles: {len(model)}")

# ----------------------------
# Accuracy Evaluation
# ----------------------------
def accuracy(model, test_data):
    correct = 0
    total = len(test_data)

    for sample in test_data:
        point = sample[:-1]
        true_label = sample[-1]

        predicted = None
        for r in model:
            if all(r[j][0] <= point[j] <= r[j][1] for j in range(len(point))):
                predicted = r[-1]
                break

        if predicted is None:
            predicted = min(model, key=lambda r: rect_distance(r, point))[-1]

        if predicted == true_label:
            correct += 1

    return (correct / total) * 100.0

acc = accuracy(model, test_data)
print(f"Model Accuracy = {acc:.2f}%")


