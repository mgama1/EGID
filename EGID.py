
#dependencies you might not have:
# install: pip install --upgrade arabic-reshaper
# install: pip install python-bidi
#ref:https://gist.github.com/amrza/04658c71ac02d82580855f89b9b3dff4

#imports
import yaml
import glob
from random import randint,choice
from PIL import Image,ImageDraw,ImageFont
import arabic_reshaper
from bidi.algorithm import get_display
import os
import numpy as np
from tensorflow.keras.preprocessing.image import ImageDataGenerator
class GenerateID():

    def __init__(self,images_num,augment=False,augment_batches=10) :
        self.images_num=images_num
        self.augment=augment
        self.augment_batches=augment_batches

        self.loadFiles()
        if not os.path.exists("./EGID_data/IDs"):
                os.makedirs("./EGID_data/IDs")

        for i in range(images_num):
            self.generateID(f"./EGID_data/IDs/ID{i}.png",f"./EGID_data/IDs/IDB{i}.png")
            print('█' * int(i/(images_num-1)*20) + '░' * int(20-(i/(images_num-1) *20)), end="\r")
        print(f"\ngenerated {images_num} ID")
        if self.augment:
            self.dataAugmentation()

    def generateID(self,front_output_path,back_output_path):
              
        person=self.generateName()
        first_name=person["first_name"]
        paternal_names=person['paternal_names']
        gender=person['gender']
        birthdate=self.generateBirthdate()
        birthdate_formatted="{YY}/{MM}/{DD}".format(YY=birthdate[-4:],MM=birthdate[2:4],DD=birthdate[:2])
        id_number=self.generateIDNumber(birthdate)

        first_name_image =self.putArText('./IDBLANK.jpg',25,first_name,(850,420))
        self.putArText(first_name_image,25,paternal_names,(850,460))
        self.putArText(first_name_image,25,self.generateAddress(),(850,500))
        self.putArText(first_name_image,25,self.generateGov(),(850,550))
        self.putArNumText(first_name_image,25,birthdate_formatted,(400,630))
        self.putArNumText(first_name_image,25,id_number,(850,650))

        first_name_image.paste(self.generateImage(gender), (240,365))
        first_name_image.save(front_output_path)

        #back id
        issue_date=self.generateIssueDate()
        back_id=self.putArNumText('./IDBACKBLANK.jpg',25,id_number,(750,345))
        self.putArNumText(back_id,25,issue_date,(480,345))
        exp_text="البطاقة سارية حتى"
        job_text="طبيب"
        self.putArText(back_id,22,exp_text,(760,510))
        self.putArNumText(back_id,25,self.generateExpirationDate(issue_date),(570,520))
        self.putArText(back_id,22,job_text,(750,365))
        if gender==1:
            gender_text="ذكر"
        else:
            gender_text="أنثى"
        self.putArText(back_id,22,gender_text,(750,450))   

        back_id.save(back_output_path)


    def loadFiles(self):
        #loadibg files :names, governorates, and images paths
        with open('names.yaml', 'r', encoding='utf-8') as file:
            names_dict = yaml.safe_load(file)
        self.male_names=names_dict["male_names"]
        self.female_names=names_dict["female_names"]
        with open('egy_gov.yaml', 'r', encoding='utf-8') as file:
            gov_dict = yaml.safe_load(file)
        self.gov_names = gov_dict['egyptian_governorates']

        self.female_images=glob.glob("./images/females/**")
        self.male_images=glob.glob("./images/males/**")


    def generateBirthdate(self):
        '''
        Generates random Birthdate
        Args:
            None
        Returns:
            birthdate(str) in format DDMMYYYY
        '''
        day=randint(1,31)
        month=randint(1,12)
        year=randint(1961,2008)
        
        birthdate="{:02}{:02}{}".format(day,month,year)
        return birthdate



    


    def generateIDNumber(self,birthdate):
        '''
        Generates random ID number based on a birthdate
        Args:
            birthdate(str): DDMMYYYY
        Returns:
            id_number(str): {century_indicator} {YY} {MM} {DD} {tailing_number}
        '''
        birthdate_year=birthdate[-4:]
        if int(birthdate_year)<2000:
            century_indicator="2"
        else:
            century_indicator="3"
        YY=birthdate[-2:]
        MM=birthdate[2:4]
        DD=birthdate[:2]
        tailing_number=str(randint(1000000,9999999))
        id_number=f"{century_indicator} {YY} {MM} {DD} {tailing_number}"
        return id_number 






    def generateGov(self):
        '''
        chooses a random governorate from  gov_names list
        Args:
            None
        Returns:
            governorate name(str)
        '''
        return choice(self.gov_names)




    def generateName(self):
        '''
        generates male and female names randomly drawn from male_names and female_names lists
        Args:
            None
        Returns:
            dict with keys: first_name, paternal_names, gender
        '''
        #baby is a girl or a boy?
        gender=randint(0,1)
        if gender==1:
            first_name=choice(self.male_names)
        else:
            first_name=choice(self.female_names)
        paternal_names=""
        for i in range(4):
            paternal_names+= choice(self.male_names)+" "
        
        return {'first_name':first_name, 'paternal_names':paternal_names,'gender':gender}



    def generateImage(self,gender):
        '''
        chooses a random image based on gender
        Args:
            gender(int): male=1, female=0
        Returns:
            pil grayscale image with size (175,175)
        '''
        
        if gender==1:
            return Image.open(choice(self.male_images)).resize((175,175)).convert("L")
        else:
            return Image.open(choice(self.female_images)).resize((175,175)).convert("L")
    



    def generateAddress(self):
        '''
        Generates not so random addresses
        Args:
            None
        Returns:
            sharee el gomhorya(str)
        '''
        
        return "شارع الجمهورية"







    def putArText(self,img,font_size,text,position):
        '''
        writes Arabic text on an image
        Args:
            img: either an image path(str) or pil image
            font_size(int)
            text(str)
            position(tuple or list)
        Returns
            pil image
        '''
        if type(img)==str:
            self.image = Image.open(img)
        else:
            self.image=img
        font = ImageFont.truetype('/usr/share/fonts/Noto_Sans_Arabic/static/NotoSansArabic-Medium.ttf', font_size)
        reshaped_text = arabic_reshaper.reshape(text)  # correct its shape
        bidi_text = get_display(reshaped_text)  # correct its direction
        # start drawing on image
        draw = ImageDraw.Draw(self.image)
        text_length = draw.textlength(bidi_text, font=font)
        draw.text((position[0]-text_length, position[1]), bidi_text, (0, 0, 0), font=font)
        
        return self.image
        


    def putArNumText(self,img,font_size,text,position):
        '''
        writes Eastern Arabic Numerals on an image
        Args:
            img: either an image path(str) or pil image
            font_size(int)
            text(str)
            position(tuple or list)
        Returns
            image
        '''
        if type(img)==str:
            self.image = Image.open(img)
        else:
            self.image=img
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", font_size)

        western_to_eastern_ar_numerals = {
            '0': '٠',
            '1': '١',
            '2': '٢',
            '3': '٣',
            '4': '٤',
            '5': '٥',
            '6': '٦',
            '7': '٧',
            '8': '٨',
            '9': '٩',
            " ": " "
        }
        eastern_arabic = ''.join([western_to_eastern_ar_numerals.get(char, char) for char in text])
        
        # start drawing on image
        draw = ImageDraw.Draw(self.image)
        text_length = draw.textlength(eastern_arabic, font=font)
        draw.text((position[0]-text_length, position[1]), eastern_arabic, (0, 0, 0), font=font)
        
        return self.image

    def generateIssueDate(self):
        year=randint(2016,2023)
        month=randint(1,12)
        return "{:02}/{:02}".format(year,month)

    def generateExpirationDate(self,issue_date):
        return f"{int(issue_date[:4])+7}/{int(issue_date[5:7])-1:02}/31"

    def dataAugmentation(self):

        # Define augmentation parameters
        datagen = ImageDataGenerator(
            rotation_range=90,
            width_shift_range=0.2,
            height_shift_range=0.2,
            shear_range=0.2,
            zoom_range=0.2,
            horizontal_flip=True,
            vertical_flip=True,
            brightness_range=[0.5, 1.2], 
            preprocessing_function=self.random_grayscale ,
            fill_mode='nearest'
        )

        # Specify the path to your dataset
        dataset_path = './EGID_data/'

        # Create a generator for your dataset
        augmented_generator = datagen.flow_from_directory(
            dataset_path,
            target_size=(1080, 1080),  # Reshape images to 224x224
            batch_size=32,
            class_mode='categorical',
            save_to_dir='./EGID_data/IDs',
            save_prefix='augmented',
            save_format='jpeg'
        )

        # Generate and save augmented images
        for i in range(self.augment_batches):  # Generate n batches of augmented images
            batch = augmented_generator.next()
            print(f'generated {i+1} batches of augmented images',end="\r")

    def random_grayscale(self,img):
            if np.random.rand() < 0.5:  # 50% chance of applying grayscale
                img = np.dot(img[..., :3], [0.2989, 0.5870, 0.1140])
                img = np.stack((img,)*3, axis=-1)  # Convert grayscale image to 3 channels
            return img