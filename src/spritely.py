#!/usr/bin/env python

import os, pprint, random, copy

from PIL import Image

key_extraction_algorithms = {
    'greatest_side': lambda i: max(i[1], i[2]),
    'greatest_area': lambda i: i[1]*i[2],
    'greatest_height': lambda i: i[2],
    'greatest_width': lambda i: i[1],
    'random': lambda i: random.choice(i[1:3]),
}

def get_image_dimensions(image_paths):
    sizes = []
    for path in image_paths:
        image = Image.open(path)
        width, height = image.size
        sizes.append((path, width, height))

    return sizes

def binpack_layout(dimensions):
    blank_tree_node = { 
        'x': 0, 'y': 0, 'w': 0, 'h': 0, 
        'bottom': None, 'right': None, 'image': None, }

    def insert(tree, dimension):
        # tree:
        if tree is None: 
            # case: null leaf
            return None

        image_w, image_h = dimension[1], dimension[2]
        if tree['image'] is not None:
            # case: image already exists at this node; traverse
            print('image exists in this space')
            return insert(tree['bottom'], dimension) or insert(tree['right'], dimension)
        if image_w > tree['w'] and image_h > tree['w']:
            # case: image larger than space in width and/or height
            print('image greater than space')
            return insert(tree['bottom'], dimension) or insert(tree['right'], dimension)
        if image_w == tree['w'] and image_h == tree['h']:
            print('exact fit')
            # case: image fits eactly in space
            tree['image'] = dimension
            return (tree['x'], tree['y'])
        elif image_w <= tree['w'] and image_h <= tree['h']:
            print('subdividing...')
            # case: image is smaller than space in width and/or height
            bottom = copy.deepcopy(blank_tree_node)
            right = copy.deepcopy(blank_tree_node)

#            print (tree['h'], dimension)
            # bottom is full original width
            bottom['x'] = tree['x']
            bottom['y'] = tree['y'] + dimension[2]
            bottom['w'] = tree['w'] 
            bottom['h'] = tree['h'] - dimension[2]
            if 0 in (bottom['h'], bottom['w']): bottom = None
            # right is reduced height, width
            right['x'] = tree['x'] + dimension[1]
            right['y'] = tree['y']
            right['w'] = tree['w'] - dimension[1] 
            right['h'] = dimension[2]
            if 0 in (right['h'], right['w']): right = None

            tree['bottom'] = bottom
            tree['right'] = right
            tree['image'] = dimension
            return (tree['x'], tree['y'])

        return None

    def grow(w, h, dimension):
        if 0 in (w, h):
            # case: empty tree; first image
            tree = copy.deepcopy(blank_tree_node)
            tree['w'], tree['h'] = dimension[1], dimension[2]
            return tree
        else:
            # case: subsequent images
            can_grow_right = h >= dimension[2]
            grow_right = copy.deepcopy(blank_tree_node)
            grow_right['x'], grow_right['y'] = w, 0
            grow_right['w'], grow_right['h'] = dimension[1], h
            right_area = grow_right['w'] * grow_right['h']

            can_grow_down = w >= dimension[1]
            grow_down = copy.deepcopy(blank_tree_node)
            grow_down['x'], grow_down['y'] = 0, h
            grow_down['w'], grow_down['h'] = w, dimension[2]
            down_area = grow_down['w'] * grow_down['h'] 

            if (not can_grow_down) and can_grow_right:
                return grow_right
            elif (not can_grow_right) and can_grow_down:
                return grow_down
            else:
                right_aspect = min(grow_right['w'], grow_right['h']) / max(grow_right['w'], grow_right['h'])
                down_aspect = min(grow_down['w'], grow_down['h']) / max(grow_down['w'], grow_down['h'])
                return grow_right if right_aspect > down_aspect else grow_down 

    tree = copy.deepcopy(blank_tree_node)

    h, w = 0, 0
    layout = []
    trees = [tree]

    for d in dimensions:
        res = None
        for tree in trees:
            res = insert(tree, d)
            if res: break;
        if res is None:
            print 'grow'
            tree = grow(w, h, d)
            pprint.pprint(tree)
            pprint.pprint(d)
            trees.append(tree)
            res = insert(tree, d)
        x, y = res
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
    res = Image.new('RGBA', (w, h), (0,255,0,255))

    for img_data in layout:
        image = Image.open(img_data[0])
        res.paste(image, (img_data[1], img_data[2])) 

    return res

def main():
    img_dir = 'test'

    files = [os.path.join(img_dir, img) for img in os.listdir(img_dir)]
    dims = get_image_dimensions(files)
    dims.sort(cmp=lambda a, b: a-b, key=key_extraction_algorithms['greatest_area'], 
        reverse=True)
#    layout = linear_layout(dims)
#    layout = linear_layout(dims, horizontal=False)
    layout = binpack_layout(dims)
    binpack_h, binpack_w = layout[1], layout[2]
    total_image_area = sum(map(lambda d: d[1]*d[2], dims))
    binpack_area = binpack_h*binpack_w
    print('total image area: {}'.format(total_image_area))
    print('binpack area: {}'.format(binpack_area))
    print('fill rate: {}'.format((total_image_area*1.0)/(binpack_area*1.0)))
    pprint.pprint(layout)
    res = composite_layout(layout)
    res.save('output.png') 

if __name__ == '__main__':
    main()
