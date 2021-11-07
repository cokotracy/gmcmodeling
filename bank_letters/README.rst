.. image:: https://img.shields.io/badge/licence-LGPL--3-blue.svg
    :alt: License: LGPL-3

===============
Account Changes
===============

This modules do some modifications on account modules add some Objects, features and fields .


Usage
=====

# add letter of credit\n
# add letter of Guarantee\n

=================
CONTRIBUTORS LIST
=================
>Analysis:
    - Mostafa Abd EL Fattah <mabdelfattah@zadsolutions.com>\n

>Development:
    - Ahmed Salama <mailto:asalama@zadsolutions.com>\n

=====================
Technical Requirements:
=====================
  > Go to Accounting -> Bank Letters -> Letter Of Credit

- Technical Requirements :-

  1> change field string in the form called Analytic Account/Project -> Make it Analytic Account

  2> Adjust those fields in Letter Of Credit form :-

     A> Add Two fields in one line like this     Margin "Float" % Amount "Float" position of that field beside value

     B> Change field label from Value to PO Value

     C> Make Amount calculated automatically with the ability to edit Amount = Margin % * PO Value

     C> Under Bank Expense Value field Add New field called Managerial Expense Value "Float field"

     D> Rename field of Commission fee expense and make it Bank Expense Account

     E> Add new field called Managerial Expense Account under the previous account "D" "many2one" with account.account

     F> Rename Irrevocable liabilities to LC Account

     G> Add new field called Loans Account under the previous account "F" "many2one" with account.account

  3> Create New Menu item Called "LC & Form 4 Configuration" Under Bank Letters

        A> This Menu item accessable by Accounting Adviser Group

        B> Inside that create new model called "bnk.lc.config" with below fields :-

             - LC Account "many2one" with "account.account"

             - Loans Account "many2one" with "account.account"

             - Bank Expense Account "many2one" with "account.account"

             - Managerial Expense Account "many2one" with "account.account"

   4> In letter of Credit Form

        A> Make all four fields Account in the form view "LC - Bank - Managerial - Loans" readonly and get their value automatically from                 LC Configuration

    5> Upon Validate the letter of credit

         Note #1: Current Scenario system generates two journal entries you will see them on smart button after validation

         Note #2: We will change that scenario by generate one journal entry instead of two with below information in journal items

         Note #3: Adjustment in journal entry will be done in journal items only, the rest of the form will be the same

         A> Items will be as follow in values

              1> Account -> "Bank Expense Account"  Value -> Bank Expense Value   "Debit"          Ex.. 2000

              2> Account -> "Managerial Expense Account" Value -> "Managrial Expense Value" Debit    Ex...3000

              3> Account -> "LC Account" Value -> "Amount After Margin" Debit    Ex.... 100000

              4> Account -> "The Bank Related Account"  Value -> "Sum of Bank, Managerial and LC Amount"   Credit     Ex.... 105000   "Put                                         the Analytic Account here"

   6> We will add a new button after validate called "Release"

        A> This button will open a wizard contains

             1 > Shipment Amount "Float"    Ex... 300000

             2 > LC Amount Deducted "Float"     Ex..... 30000

             3 > Loan "Computed" Shipment Amount - LC Amount Deducted   Ex...... 270000

             4 > Two Buttons as usual in wizard "Ok" and "Cancel"

         B> After that state must be changed to LC Released

          Note #1: This button will be pressed several time or may be one time

          Note #2 : the incoming requirement #C will be done each time we pressed the button

          Note #3 : You have to create Tab Called LC History to record the values of Release button each time you pressed

          Note#4 : Upon that history we need to put validation here to make sure the total of all shipment amount never exceed the PO                                 Value and the All LC Amount Deducted Never Exceed The Amount After Margin

          Note#5 : Checking the rule will be done each time we release LC if the rule is True and the amount exceeds raise warning

                         "You Can not proceed with shipment amount above PO value"

         C> A new Journal Entry must be generated with below items

               1> Account -> "Partner Payable Account"you will find that account in partner form accounting Tab"  Value -> "Shipment                                 Amount"     Debit    Ex.... 300000     "Put the related Partner Here"

               2> Account -> "LC Account" Value -> " LC Amount Deducted"  Credit      Ex....30000   "Put the related Partner Here"

               3> Account -> "Loans Account"  Value -> "Loan Value"    Credit     Ex... 270000   "Put the analytic Account Here" + "Put the End date                        in front of Due Date"    + "Put the related Partner Here"

This module is maintained by the Zad.


To contribute to this module, please visit http://zadsolutions.com.
