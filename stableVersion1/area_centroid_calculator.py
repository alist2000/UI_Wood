def calculate_centroid_and_area(points, magnification_factor):
    print(points)
    num_points = len(points)
    area = 0
    centroid_x = 0
    centroid_y = 0

    for i in range(num_points):
        j = (i + 1) % num_points
        xi, yi = points[i]
        xj, yj = points[j]

        cross_product = xi * yj - xj * yi
        print(cross_product)
        area += cross_product
        centroid_x += (xi + xj) * cross_product
        centroid_y += (yi + yj) * cross_product

    area *= 0.5
    centroid_x /= (6 * area)
    centroid_y /= (6 * area)

    return centroid_x / magnification_factor, centroid_y / magnification_factor, abs(area) / (magnification_factor ** 2)
