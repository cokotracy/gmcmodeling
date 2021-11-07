.. class:: text-left

Sale Jobs
=========

Adding Feature of jobs in sales order.


Features
--------
1 - In Quotation Form View add those fields

    A - Job Type -> Many2one field with job.type

    B - Project Name -> Many2one with project.project and it cames automatically from related Job Estimate Project field

    C- Create smart button inside quotation for related job estimates

    D- Project No -> Char field -> Came automatically from related project No field which you will find inside project information

    E- Project Beginning Date -> Date field -> Came automatically from related project Beginning date field which you will find inside project information.

    F- Project Ending Date -> Date field -> Came automatically from related project Ending date field which you will find inside project information.
    G-  Project Period -> Char field -> Came automatically from related project period date field which you will find inside project information.


2 - In Job Estimate Form view add smart button to show related quotation to the job estimate.

3 - In Quotation Order line add those fields

      A- Change Product Name to Work item.

      B - Recently Done -> Float field add that after Ordered Quantity field ->  In Case of the product type is service and upon putting value in that field we need to increment the Delivered Quantity field with the value after saving the Quotation



4- In Related Customer Invoice Add those fields and do these changes

     A- Add Project Name (many2one with project.project) field which came from related quotation project name

     B- Add Project No. (char field) field which came form related quotation project no.

     C- Add Project Beginning Date field (Date field)  which came from related quotation project beginning date field

     D- Add Project Ending Date field (Date field)  which came from related quotation  Project Ending Date field.

     E- Add Project Period field (Char field) which came from related quotation project period field.

     F- Job Type field (many2one with job.type) which came from related quotation job type.

     G- Sub Contractor Invoice (Char field) which increment automatically from 1 - 2 - 3 and so on according to how many invoices created for one quotation and note if i create one invoice and delete it mustn't be counted.

     H- Period From (Date field)

     I- Period To (Date field)



5- In Related Customer invoice Lines :-

    A - Rename the Quantity to Current QTY

    B- Change the product to Work Item

    C- Before Current Quantity add Previous QTY Float field (Came Automatically from Previous Invoice Current QTY on the same product on the same Quotation)

    D- After Previous QTY add Total Contract QTY float field which came from Related Quotation Ordered Quantity

    E- After Current QTY add Total QTY Float field which came from equation [ Current QTY + Previous Quantity ]

    F- Add % Completed Float field

    G- Change Amount to be Current Amount

    H- Add Total Amount after current amount which calculated from [ Total QTY * Unit Price ]

 6- In related Customer Invoice

     A- Change the Total String field to be Net to be paid

.. class:: text-left

Credits
-------

.. |copy| unicode:: U+000A9 .. COPYRIGHT SIGN

- `Omar Abdelaziz <umar_3ziz@hotmail.com>`_ |copy|
