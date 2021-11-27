### Power Plant Monitoring System (PPMS)
#### Video Demo:  https://youtu.be/B977uL-xTLo
#### Description: 
###### Implemented using PyCharm. 
In power plants there are lots of equipments such as pumps, motors, fans, valves, filters, boilers & much more.
Different engineering teams perform different maintenance activity on these equipments.
Also, some of these equipments have different operating regime than others.

To make it easier for the engineers to check the maintenance history and for the operator to check the operation regime
I created this webpage which allow engineers to add equipment and generate QR code for this equipment in order to
print it and pin it on the equipment on site so that its history and operation regime are easy to access by scanning the
Qr Code pinned on that equipment.

#### Quick walk-through:

- Register / Login:

    These pages allow the engineer to register and login to the webpage but only when username, password & engineer position
    are submitted, since some pages within the webpage are only accessible depending on position. users are added to users table in database
    with unique id and hashed password.

- Home Page:

    In this page, all added equipment are displayed from database with their Qr Code image, anyone can print out the image and pin it
    on equipment at the work site.

- Add Equipment Page:
    
    This page allows engineers to add new equipment, it will generate a QR code for this equipment, add it to equipment table in the database and redirect the user
    to homepage with new equipment displayed along with its QR Code.

- Maintenance History Page:
    
    This page is used to add any maintenance activity done on the equipment along with the date, a select list is
    implemented to select equipment from the database. Maintenance activity is added to table named history in the database which is linked to equipment
    table via equipment id.
    only maintenance engineers are allowed to enter this page.

- Operation Page:

    This page is used to add equipment operation regime, a select list is
    implemented to select equipment from the database. Operation regime is added to table named operation in the database which is linked to equipment
    table via equipment id.
    only Performance and efficiency engineers are allowed to enter this page.

- View Equipment Page:
    
    In this page you can upload the QR code of any equipment to view its maintenance history and operation regime.

- Cam Page:

    In this page there is a button to open the device camera and scan the QR Code pinned on the equipment to view its maintenance history and operation regime.


Thank You Very Much And this Was CS50 =D ! 