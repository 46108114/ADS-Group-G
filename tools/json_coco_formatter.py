import argparse
import glob
import json
import os
import shutil

from imutils import paths

def get_args():
    parser = argparse.ArgumentParser(description='Clean DataTorch COCO JSON file')
    parser.add_argument('-i', '--input', required=True,
                        help='DataTorch JSON File')
    parser.add_argument('-p', '--path', required=True,
                        help='Input Images Folder Path')
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

def clean_json_dict(json_dict, image_path):
    # Gather Filenames of Images included in input image path directory
    filename_list = [filename.split('/')[-1] for filename in glob.glob("{}/*.*".format(image_path))]

    # Remove images not part of the input image path directory
    json_dict['images'] = [image for image in json_dict['images'] if image['path'] in filename_list]
    
    # Gather all image_ids of remaining images
    image_ids = [image['id'] for image in json_dict['images']]

    # Remove annotations not part of image_ids list
    json_dict['annotations'] = [annotation for annotation in json_dict['annotations'] if annotation['image_id'] in image_ids]

    # Return Clean JSON Data
    return json_dict

def main():
    args = get_args()
    json_path = args.input
    image_path = args.path

    # Datasets to Export
    dataset_list = []
    
    # Read json file
    with open(json_path, 'r') as fp:
        coco_dict = json.load(fp)
    
    # Clean coco_dict
    coco_dict = clean_json_dict(coco_dict, image_path)

    coco_dict['info']['description'] = 'ADS_Project Dataset'
    coco_dict['licenses'] = [{'name': '', 'id': 0, 'url': ''}]
    coco_dict['categories'][0]['supercategory'] = 'person'

    # Add License for each image, rename each image accordingly and remove unnecessary keys
    if not os.path.exists(image_path + 'renamed_images/'): os.makedirs(image_path + 'renamed_images/')

    for image in coco_dict['images']:
        image['license'] = 0
        image.pop('datatorch_id', None)
        image.pop('storage_id', None)
        image.pop('path', None)
        shutil.copyfile(image_path + image['file_name'], image_path + 'renamed_images/' + str(image['id']).zfill(12) + '.jpg')
        # os.rename(image_path + image['file_name'], image_path + 'renamed_images/' + str(image['id']).zfill(12) + '.jpg')
        image['file_name'] = str(image['id']).zfill(12) + '.jpg' 

    # Clean annotations
    for annotation in coco_dict['annotations']:
        # Clean possible human error for person bounding box
        # annotation_image = coco_dict['images'][annotation['image_id']-1] 

        for image in coco_dict['images']:
            if image['id'] == annotation['image_id']:
                annotation_image = image

        bbox_new, area_new = clean_person_bb(annotation, annotation_image)
        # annotation['bbox'], annotation['area'] = clean_person_bb(annotation, annotation_image)

        if bbox_new != annotation['bbox'] or area_new != annotation['area']:
            # print(annotation['bbox'], annotation['area'])
            # print(bbox_new, area_new)
            annotation['bbox'], annotation['area'] = bbox_new, area_new

        # Clean keypoint annotations
        annotation['keypoints'], annotation['num_keypoints'] = clean_keypoints(annotation)

        # Remove unneccessary annotation keys
        annotation['segmentation'] = [[]]
        annotation.pop('datatorch_id', None)
        
    # Display Annotations numbers that don't have Keypoints attribute
    annotation_list = []
    for annotation in coco_dict['annotations']:
        if 'keypoints' not in annotation.keys():
            print(annotation['image_id'])
            annotation_list.append(annotation['image_id'])
    if len(annotation_list) != 0: print("Annotations without Keypoints:", annotation_list)

    filename = json_path.split('/')[-1]
    with open('Clean_' + filename, 'w') as fp:
        json.dump(coco_dict, fp, indent=2, sort_keys=True)

if __name__ == "__main__":
    main()