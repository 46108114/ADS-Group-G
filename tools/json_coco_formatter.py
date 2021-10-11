import json
import argparse

def get_args():
    parser = argparse.ArgumentParser(description='Clean DataTorch COCO JSON file')
    parser.add_argument('-i', '--input', required=True,
                        help='DataTorch JSON File')
    return parser.parse_args()

def clean_person_bb(annotation, image_info):
    # Input of annotation dictionary
    bbox_x, bbox_y, bbox_w, bbox_h = annotation['bbox']

    bbox = annotation['bbox']
    area = annotation['area']
    w = image_info['width']
    h = image_info['height'] 

    if bbox_x < 0 or bbox_y < 0 or (bbox_x+bbox_w) > w or (bbox_y+bbox_h) > h:
        bbox_x_new = max(0, bbox_x)
        bbox_y_new = max(0, bbox_y)
        bbox_w_new = bbox_w if bbox_x == bbox_x_new else (bbox_w+bbox_x)
        bbox_h_new = bbox_h if bbox_y == bbox_y_new else (bbox_h+bbox_y)
            
        bbox = [bbox_x_new, bbox_y_new, bbox_w_new, bbox_h_new]
        area = bbox_w_new * bbox_h_new
            
        if (bbox_x_new+bbox_w_new) > w or (bbox_y_new+bbox_h_new) > h:
            bbox_w_new = min(bbox_w, w-bbox_x_new)
            bbox_h_new = min(bbox_h, h-bbox_y_new)

            bbox = [bbox_x_new, bbox_y_new, bbox_w_new, bbox_h_new]
            area = bbox_w_new * bbox_h_new
        
    return bbox, area 

def clean_keypoints(annotation):
    bbox_x, bbox_y, bbox_w, bbox_h = annotation['bbox']
    bbox_xmax = bbox_x + bbox_w
    bbox_ymax = bbox_y + bbox_h
    keypoints = annotation['keypoints']

    num_keypoints = 17
    for i in range(0, 51, 3):
        [keypoint_x, keypoint_y, keypoint_v] = keypoints[i:i+3]

        if keypoint_x > bbox_xmax or keypoint_x < bbox_x or keypoint_y > bbox_ymax or keypoint_y < bbox_y:
            keypoints[i], keypoints[i+1], keypoints[i+2] = 0, 0, 0 
            num_keypoints-=1
        else:
            # Update Visibility flag to 2 (Labeled and Visible)
            keypoints[i+2] = 2

    return keypoints, num_keypoints

def main():
    args = get_args()
    json_path = args.input

    # Read json file
    with open(json_path, 'r') as fp:
        coco_dict = json.load(fp)
    
    coco_dict['info']['description'] = 'ADS_Project Dataset'
    coco_dict['licenses'] = [{'name': '', 'id': 0, 'url': ''}]
    coco_dict['categories'][0]['supercategory'] = 'person'

    # Add License for each image and remove unnecessary keys
    for image in coco_dict['images']:
        image['license'] = 0
        image.pop('datatorch_id', None)
        image.pop('storage_id', None)
        image.pop('path', None)
    
    # Clean annotations
    for annotation in coco_dict['annotations']:
        # Clean possible human error for person bounding box
        annotation_image = coco_dict['images'][annotation['image_id']-1] 
        bbox_new, area_new = clean_person_bb(annotation, annotation_image)
        # annotation['bbox'], annotation['area'] = clean_person_bb(annotation, annotation_image)

        if bbox_new != annotation['bbox'] or area_new != annotation['area']:
            print(annotation['bbox'], annotation['area'])
            print(bbox_new, area_new)
            annotation['bbox'], annotation['area'] = bbox_new, area_new

        # Clean keypoint annotations
        annotation['keypoints'], annotation['num_keypoints'] = clean_keypoints(annotation)

        # Remove unneccessary annotation keys
        annotation['segmentation'] = [[]]
        annotation.pop('datatorch_id', None)
        
    filename = json_path.split('\\')[-1]
    with open('clean_' + filename, 'w') as fp:
        json.dump(coco_dict, fp, indent=2, sort_keys=True)

if __name__ == "__main__":
    main()