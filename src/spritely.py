#!/usr/bin/env python

import os, pprint, random, copy

from PIL import Image

key_extraction_algorithms = {
    'greatest_side': lambda i: max(i[1], i[2]),
    'greatest_area': lambda i: i[1]*i[2],
    'greatest_height': lambda i: i[1],
    'greatest_width': lambda i: i[2],
    'random': lambda i: random.choice(i[1:3]),
}

def get_image_dimensions(image_paths):
    sizes = []
    for path in image_paths:
        image = Image.open(path)
        width, height = image.size
        sizes.append((path, width, height))

    return sizes

#def pack_space(x, y, w, h, images):
#    # return list of image positions and remaining images
#    pass
#
#def layout_images(dimensions):
#    ox, oy = 0, 0
#    layout = {}
#
#    for i, d in enumerate(dimensions):
#        if i == 0: 
#            # first image, place at origin
#            layout[d[0]] = 0,0
#            ox, oy = d[1], d[2]
#        else:
#            # non-first image; compute position
#            area = d[1]*d[2]
#            # compute right-branch scenario
#            # compute bottom-branch scenario

def binpack_layout(dimensions):
    blank_tree_node = { 
        'x': 0, 'y': 0, 'w': 0, 'h': 0, 
        'bottom': None, 'right': None, 'image': None, }

    def insert(tree, dimension):
        # tree:
        # * x, y, w, h, bottom, right, image
#        pprint.pprint(tree)
        if tree is None: 
            # case: null leaf
            return None

        image_w, image_h = dimension[1], dimension[2]
        if tree['image'] is not None:
            # case: image already exists at this node; traverse
            print('image exists in this space')
            return insert(tree['bottom'], dimension) or insert(tree['right'], dimension)
#            return insert(tree['right'], dimension) or insert(tree['bottom'], dimension)
        if image_w > tree['w'] and image_h > tree['w']:
            # case: image larger than space in width and/or height
            print('image greater than space')
            return insert(tree['bottom'], dimension) or insert(tree['right'], dimension)
#            return insert(tree['right'], dimension) or insert(tree['bottom'], dimension)
        if image_w == tree['w'] and image_h == tree['h']:
            print('exact fit')
            # case: image fits eactly in space
            tree['image'] = dimension
            return (tree['x'], tree['y'])
        elif image_w <= tree['w'] and image_h <= tree['h']:
            print('subdividing...')
            # case: image is smaller than space in width and/or height
#            tree['w'], tree['h'] = dimension[1], dimension[2]
            bottom = copy.deepcopy(blank_tree_node)
            right = copy.deepcopy(blank_tree_node)

            print (tree['h'], dimension)
            # bottom is full original width
            bottom['x'] = tree['x']
            bottom['y'] = tree['y'] + dimension[2]
            bottom['w'] = tree['w'] 
            bottom['h'] = tree['h'] - dimension[2]
            # right is reduced height, width
            right['x'] = tree['x'] + dimension[1]
            right['y'] = tree['y']
            right['w'] = tree['w'] - dimension[1] 
            right['h'] = dimension[2]

            tree['bottom'] = bottom
            tree['right'] = right
            tree['image'] = dimension
            return (tree['x'], tree['y'])

        return None

    sum_w = sum(map(lambda d: d[1], dimensions))
    sum_h = sum(map(lambda d: d[2], dimensions))
    tree = copy.deepcopy(blank_tree_node)
    tree['w'], tree['h'] = sum_w, sum_h

    h, w = 0, 0
    layout = []
    for d in dimensions:
        x, y = insert(tree, d)
        w = max(w, x+d[1])
        h = max(h, y+d[2])
        layout.append((d[0], x, y))

    return (layout, w, h) 

def linear_layout(dimensions, horizontal=True):
    layout = []
    w, h = 0, 0
    for i, d in enumerate(dimensions):
        if horizontal:
            layout.append((d[0], w, 0))
            w += d[1]
            h = max(h, d[2])
        else:
            layout.append((d[0], 0, h))
            w = max(w, d[1])
            h += d[2]

    return layout, w, h 

def composite_layout(layout):
    layout, w, h = layout
    res = Image.new('RGBA', (w, h), (255,255,255,255))

    for img_data in layout:
        image = Image.open(img_data[0])
        res.paste(image, (img_data[1], img_data[2])) 

    return res

def main():
    """docstring for main"""

    img_dir = 'test'

    files = [os.path.join(img_dir, img) for img in os.listdir(img_dir)]
    dims = get_image_dimensions(files)
    dims.sort(cmp=lambda a, b: a-b, key=key_extraction_algorithms['greatest_side'], 
        reverse=True)
#    layout = linear_layout(dims)
#    layout = linear_layout(dims, horizontal=False)
    layout = binpack_layout(dims)
    pprint.pprint(layout)
    res = composite_layout(layout)
    res.save('output.png')



if __name__ == '__main__':
    main()
