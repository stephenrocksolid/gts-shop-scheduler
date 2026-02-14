**Classic Accounting**

```
©
```
_User's Manual_

```
By Joseph A Miller
```

```
2 CA User Manual
```

**Classic Accounting
©**

_User's Manual_

```
By Joseph A Miller
```

## Preface.........................................................................................................

This document is intended to be an Owner's Manual / User Guide for Classic
Accounting©.

Classic Accounting© is a Java / PostgreSQL based Accounting Software that is
designed, owned and maintained by **Conservative Technology Services, Inc.**
(referred to as CTS in this document).

This document **Copyright** © 2015-2024 by Conservative Technology Services,
Inc.

**Disclaimer** :

The Author is not responsible if you attempt to contact any individual or
company using information displayed in the images used in this manual. The
author has a test data set that has a good deal of fact and fiction mixed together.

If you find your name in this document we hope you are not offended.
Addresses and phone numbers were scrambled and mixed on a spreadsheet
before importing in Classic Accounting, there should be no valid phone numbers
or addresses on the screenshots in this document.

Errors and typos are abundant in this document, if you make a list of the ones
you find and send it to the Author, or to Conservative Technology Services, your
input would be appreciated and acknowledged.

**Acknowledgments** :

The Author would like to Thank Alvin Witmer and his staff at VPW Enterprises
for proofreading and input. Their additions, notes and bug reports are tagged
(VPWR). Thanks to Allen Hoover Jr, for his contribution of Create a Logo for
Classic Accounting. Also thanks to Aaron Martin and all the other folks who send
suggestions and contributions.

If you are reading an electronic form of this document you can use your document
viewer's search feature (Ctrl+F) to find updates to the manual for a specific
release by searching for the version number.

```
Version 2018.1.1, April 2018 (Search for text 2018.1) Version 2018.2, December 2018
Version 2019.1, May 2019 Version 2019.2, December 2019
Version 2020.1, August 2020 Version 2020.2, May 2021
Apologies to year 2021 - no updates released
Version 2022.1, October 2022 (Chapters added and started re-arranging this document)
Version 2023.1, June 2023 (Many pictures updated)
Version 2024.1, September 2024
```

**Classic Accounting
©**

_User's Manual_

```
By Joseph A Miller
Last Updated: Sep 5, 2024
```

## General Notes...............................................................................................

This manual is optimized to be used as a PDF document and read on-screen.
The Blue Underlined Text indicates a Hyperlink, if you click on it then the view
will move to the point that the text is referencing. Here is a link to the Classic
Accounting Initial Setup Guide on page 22. If you are reading a printed copy, of
course it is just Blue Underlined Text! Most links have page numbers for
reference as well. If you use a Hyperlink to jump to another page of the
document, you can usually return to your previous page by clicking the Back

arrow at the upper left the PDF viewer.

It would be nice if entries in the Alphabetical Index of Keywords would be
Hyperlinks as well, but the author was unable to determine how to accomplish
this in a reasonably easy manner. **To go to a specific page, type the page**

**number in the page # field of the viewer and hit Enter!**

(Note: in the embedded help viewer the page number is at top, toward the left,
other PDF viewers often have it at bottom.)

The _Italic_ text usually indicates some text that is typed by the user, or
something that can be modified such as the name of a GL Account or Item.

The **Bold** text is usually something important, often the name of a control, or a
word or phrase found in the Alphabetical Index.

This User Manual is embedded in Classic Accounting! Open it with **Menu >
Help > Help** , or hit the **F1** key to open this document in a viewer as displayed
below. Unfortunately the embedded viewer's graphic rendering is not up to par
with Okular or Adobe Viewer.
Hint: The images display better if the zoom level is adjusted, try 200%.


## Table Of Contents.........................................................................................

## Table Of Contents



- Preface.........................................................................................................
- General Notes...............................................................................................
- Table Of Contents.........................................................................................
- Chapter 1: Welcome to Classic Accounting!.............................................
   - 1.1 System Requirements.......................................................................................
   - 1.2 The GUI, or User Interface................................................................................
   - 1.3 Databases..........................................................................................................
   - 1.4 Let's get connected!..........................................................................................
   - 1.5 Connection issues.............................................................................................
   - 1.6 Connection Profiles...........................................................................................
   - 1.7 Startup / Version Updates.................................................................................
   - 1.8 Classic Accounting Initial Setup Guide............................................................
   - 1.9 The Home Screen..............................................................................................
   - 1.10 General Help on Zones....................................................................................
   - 1.11 Org: People and Companies............................................................................
   - 1.12 General Help on Forms...................................................................................
   - 1.13 Saving Documents...........................................................................................
   - 1.14 Printing Documents........................................................................................
   - 1.15 Search Dialogs................................................................................................
   - 1.16 Other General Tips..........................................................................................
- Chapter 2: Startup Considerations..........................................................
   - 2.1 Securing Classic Accounting............................................................................
   - 2.2 Importing / Exporting / Updating Items...........................................................
   - 2.3 Exporting Items.................................................................................................
   - 2.4 Importing New Items........................................................................................
   - 2.5 Updating Items..................................................................................................
   - 2.6 Import / Export Addresses................................................................................
   - 2.7 Exporting Names...............................................................................................
   - 2.8 Importing Names..............................................................................................
- Chapter 3: Documents...............................................................................
   - 3.1 Types of Documents..........................................................................................
   - 3.2 Posting vs. Non-Posting....................................................................................
   - 3.3 Creating Documents.........................................................................................
   - 3.4 Saving Documents.............................................................................................
   - 3.5 Recalling Documents........................................................................................
   - 3.6 Printing Documents..........................................................................................
   - 3.7 Converting (Linking) Documents.....................................................................
   - 3.8 Copying & Pasting Documents..........................................................................
- Chapter 4: Accounting Basics...................................................................
   - 4.1 GL Accounts......................................................................................................
   - 4.2 Debits & Credits................................................................................................
   - 4.3 GL Account Types..............................................................................................
   - 4.4 Usage of various Account Types........................................................................
   - 4.5 Opening Balance of Accounts (Initial Setup)...................................................
   - 4.6 Default GL Accounts.........................................................................................
   - 4.7 Tips..................................................................................................................
   - 4.8 Financial Reports............................................................................................
   - 4.9 Transactions and their effects on GL Accounts..............................................
- Chapter 5: The Menu Bar........................................................................
   - 5.1 Menu Shortcuts...............................................................................................
   - 5.2 File Menu........................................................................................................
   - 5.3 Edit Menu........................................................................................................
   - 5.4 Company Menu................................................................................................
   - 5.5 General Ledger Menu......................................................................................
   - 5.6 Items Menu.....................................................................................................
   - 5.7 Income Menu..................................................................................................
   - 5.8 Expense Menu.................................................................................................
   - 5.9 Banking Menu.................................................................................................
   - 5.10 Payroll Menu.................................................................................................
   - 5.11 Reports Menu................................................................................................
   - 5.12 Help Menu.....................................................................................................
- Chapter 6: Item Price Calculations........................................................
   - 6.1 Markup vs. Margin..........................................................................................
   - 6.2 Price Levels.....................................................................................................
   - 6.3 Units................................................................................................................
   - 6.4 Markup Formulas............................................................................................
   - 6.5 Rounding Prices..............................................................................................
- Chapter 7: Items......................................................................................
   - 7.1 Item Types.......................................................................................................
   - 7.2 Item Manager..................................................................................................
   - 7.3 Adding and Editing Items...............................................................................
   - 7.4 Non-Inventory Item.........................................................................................
   - 7.5 Inventory Item.................................................................................................
   - 7.6 Retail Inventory Item......................................................................................
   - 7.7 Component Inventory Item.............................................................................
   - 7.8 Manufactured Inventory Item.........................................................................
   - 7.9 Service Item....................................................................................................
   - 7.10 Other Charge Item........................................................................................
   - 7.11 Sales Tax Item...............................................................................................
   - 7.12 Discount Item................................................................................................
   - 7.13 Asset Item.....................................................................................................
   - 7.14 Item Quick Edit.............................................................................................
   - 7.15 Item Bulk Edit...............................................................................................
- Chapter 8: Manufacturing.......................................................................
- Chapter 9: Expense Zone.........................................................................
   - 9.1 Vendors............................................................................................................
   - 9.2 Quote Request.................................................................................................
   - 9.3 Purchase Order...............................................................................................
   - 9.4 Item Receipt....................................................................................................
   - 9.5 Vendor Bill.......................................................................................................
   - 9.6 Vendor Credit..................................................................................................
   - 9.7 Pay Bills...........................................................................................................
- Chapter 10: Income Zone........................................................................
   - 10.1 Income Document Flow.................................................................................
   - 10.2 Customers.....................................................................................................
   - 10.3 Customer Bulk Edit.......................................................................................
   - 10.4 Estimate........................................................................................................
   - 10.5 Sales Order....................................................................................................
   - 10.6 Invoice...........................................................................................................
   - 10.7 Credit Memo..................................................................................................
   - 10.8 Receive Payment...........................................................................................
   - 10.9 Sales Receipt.................................................................................................
   - 10.10 Barcode Scanning.......................................................................................
   - 10.11 Finance Charges..........................................................................................
   - 10.12 Statements..................................................................................................
- Chapter 11: Payroll Zone.........................................................................
   - 11.1 Timecards......................................................................................................
   - 11.2 Pay Periods....................................................................................................
   - 11.3 Payroll Items.................................................................................................
   - 11.4 Employees.....................................................................................................
- Chapter 12: Banking Zone......................................................................
   - 12.1 Register.........................................................................................................
   - 12.2 Checking.......................................................................................................
   - 12.3 Deposit..........................................................................................................
   - 12.4 Transfer.........................................................................................................
   - 12.5 Reconciling your Checking Account.............................................................
- Chapter 13: Other Features.....................................................................
   - 13.1 CA Search......................................................................................................
   - 13.2 Job Tracking..................................................................................................
   - 13.3 Org Groups....................................................................................................
   - 13.4 Attachments..................................................................................................
- Chapter 14: Reports Zone.......................................................................
   - 14.1 Report Manager............................................................................................
   - 14.2 Financial Reports..........................................................................................
   - 14.3 Income & Receivables...................................................................................
   - 14.4 Expense And Payable.....................................................................................
   - 14.5 Inventory Reports..........................................................................................
   - 14.6 GL and Accountant Reports..........................................................................
   - 14.7 My Reports....................................................................................................
   - 14.8 Editing Reports.............................................................................................
   - 14.9 Company Logo...............................................................................................
- Chapter 15: How do I handle this?.........................................................
   - 15.1 Sales Tax........................................................................................................
   - 15.2 Credit Cards..................................................................................................
   - 15.3 Loans.............................................................................................................
   - 15.4 Advance Payments / Account Credit.............................................................
   - 15.5 Advance Payment to Vendor..........................................................................
   - 15.6 Receiving a Vendor Credit Refund................................................................
   - 15.7 Returned Checks...........................................................................................
- Chapter 16: FAQS....................................................................................
   - 16.1 Check Signature............................................................................................
   - 16.2 Insufficient Permission.................................................................................
   - 16.3 Receive Payments Faster...............................................................................
   - 16.4 Wrong GL Account Used...............................................................................
- Chapter 17: Troubleshooting..................................................................
- Chapter 18: Appendix..............................................................................
   - 18.1 The CA Dictionary.........................................................................................
   - 18.2 Keyboard Shortcuts.......................................................................................
- Alphabetical Index of Keywords...............................................................


# This page

# intentionally

# left blank


## Chapter 1: Welcome to Classic Accounting!.............................................

Classic Accounting will usually be referred to as **CA** in this document.
CA is known as a program, software, **application** or app. It is often referred
to as the **system** in this document.

The purpose of CA is for tracking financial information for your business (or
personal). To fully benefit from the features available you will need to track all
money going in and out of your business.

See the cover page for the current version (such as 2022.1) of Classic
Accounting. This version number changes each time CTS sends out an **update**
for CA, typically twice a year.

Note: This user manual was originally written for CA version 2.4.0 (released
May 2015). A _Release Notes_ document is provided with each CA update, so we
will not list the modifications made to each update in this manual. We will
attempt to update this manual to reflect the changes that occurred, but you will
need to read the release notes to find out what changes actually occurred in any
given release. Many of the changes made to the manual are tagged with the
version number, if you have a PDF or OpenOffice Writer version of this manual
you can search for x.x (example: 2020.2) to find the various updates made to this
manual for a given update. This should make it easier for you to find the User
Manual updates made in the latest version.

_Chapter 1: Welcome to Classic Accounting!_ **11** CA _User Manual_


### 1.1 System Requirements.......................................................................................

Classic Accounting will function on most reasonably modern computers, but
the user experience will be better if enough processing speed and memory are
available.

For testing purposes (this was a few years ago) the author installed Classic
Accounting on a Raspberry Pi Model 3B+. It works, but is really slow business!

**Disk Space**
For persistent storage (hard / solid-state drive) you will need sufficient free
space to install Java, PostgreSQL and the ClassicAcctApp.jar and reports. Plus
additional space to store accounting information as you go. While this total may
be under 1GB, you should have at least 3-5 GB free space on your disk to consider
running CA.

```
Nowadays (2024) having 3-5 GB free space means your disk is almost full.
```
**RAM (operating memory)**
It is recommended to have at least 1 GB free RAM, but more RAM is better.
Classic Accounting will operate better if more RAM is available.

Free RAM is the amount you have available after the Operating System is
loaded and you have your other "standard" applications running that you will be
using concurrently with Classic Accounting.

With a lightweight Linux distro you can operate a single instance quite nicely
on 2 GB RAM total, but Windows 10 or 11 will require 8+ GB because the
operating system uses up so much RAM.

As a rule of thumb you should probably figure around 1.5 GB free RAM per CA
instance you want to run.

The amount of data you have in CA makes a difference, a new company with
only minimal data can probably run OK on 500 MB RAM, but if you have a couple
hundred thousand items in the database CA will likely freeze up if it doesn't have
at least 1 GB RAM available to use.

**Hardware (CPU)**
The CPU (the processor) is the heart of any computer, and the faster the
better. Modern multi-core CPU's operate in the range of 3.5 – 5.0+ GHz (million
clock cycles per second), and CA benefits from this. CA will function perfectly
"correct" on an old / slow CPU, but it will operate faster and be more responsive
on a faster processor.

CA has some internal processes that will benefit from a multi-core CPU, but
the majority of the processing is done in a single thread. Having a dual (2) or
Quad (4) core CPU may be noticeably better in some operations than a single core
CPU of the same clock rate, but it's unlikely there will be any benefit above 4
cores. A 2-core CPU running at 4.0 GHz is preferable to a 4-core at 3.0 GHz.

_Chapter 1: Welcome to Classic Accounting!_ **12** CA _User Manual_


### 1.2 The GUI, or User Interface................................................................................

CA is a 2-part system. The following includes some technical details, if not all of
it makes sense, don't worry!

When you double-click the **Accounting** icon on your desktop, it opens a
window that contains a Graphical User Interface. Think what each of those words
mean, changing the order of the words might make it clearer: Interface =
something to interact with, Graphical = with pictures, User = someone who uses
(you). This is commonly called a **GUI** (pronounced "gooey") in the computer
world. The GUI is what you see and work with.

The alternative to using a GUI is using a Command Line Interface, or CLI.
Trust me, you _do not_ want to do your accounting with a CLI application. The GUI
is one part of the system, and it is written in Java. The Java we're talking about
here is a Programming Language, not a caffeine fix!

**1.2.1Multiple GUIs**
It is possible to have more then one copy (instance) of the CA GUI open on the
same machine at the same time, and they can be connected to the same or
different databases. To have 2 GUIs open that are connected to 2 different
databases you can open 2 copies of CA then use the Menu > Company > Choose
Database option to switch one of them to another database. If you do this on a
regular basis, you'll probably want to check the **Always show on Startup** option
on the Choose Database dialog, which allows you to choose the database you want
on startup.

_Chapter 1: Welcome to Classic Accounting!_ **13** CA _User Manual_


### 1.3 Databases..........................................................................................................

The other part of the system is behind the scenes, you never see it. This is the
PostgreSQL program. PostgreSQL is a **database engine** , which is a program for
storing and managing **data** , or information. The GUI connects (or "talks") to
PostgreSQL, which adds, updates, deletes or retrieves data upon request by the
user (you). PostgreSQL is one particular database engine, and a very good one.
There exist many other database engines, such as SQL Server, MySQL, Oracle,
etc.

This 2-part approach enables a **Multi-User** setup. Multiple Classic Word
Processors (up to 8 model 104As or 15 Steward / Choreboy units) can be
interconnected using network cables and a network switch. Each machine has its
own GUI, but all the GUI's connect to a single PostgreSQL database on the **server**
machine. As soon as a user adds or modifies any document and saves the
changes, those changes are visible to all other users. Only one copy of the data is
maintained, all users access it.

PostgreSQL is capable of storing and managing more then one set of data.
One set of data, as used by a business, is often referred to as a **database** , or data
set. CA can create as many databases as you desire, and gives each one a name
of your choice. You may want to have a 'test' database for trying out different
things. If you are a bookkeeper and do paperwork for more then one company,
you would create a different database for each company. When you launch CA for
the first time it may open a new database called _default_db_. When a new database
is created it has a default GL Account list set up, as well as 2 Users, _guest_ and
_admin_. For help on adding users and setting permissions see Securing Classic
Accounting on pg 59. For help on creating additional databases see Database
Utilities on page 117.

Unlike some other Accounting programs CA does not impose limits on how
much data can be stored in one database. Some programs require that you
purchase a "Premium" version in order to store more than a certain number of
Customers or Items, Classic Accounting is limited only by the storage and
computing power of the machine(s) being used and the ability of the GUI (and
network) to handle the data. Tests indicate that with sufficiently powerful
computers / processors CA can handle several hundred thousand Items and tens
of thousands of Customers.

When you launch CA it will open the database that was last used. To switch to
a different database select **Choose Database...** from the **Company** menu.

_Chapter 1: Welcome to Classic Accounting!_ **14** CA _User Manual_


### 1.4 Let's get connected!..........................................................................................

This section revised for v2023.

Before we can do anything with Classic Accounting we need to connect our
GUI (Classic Accounting) to a database (PostgreSQL).

If you purchased a Word Processor from a CTS dealer with CA installed very
likely everything is already set up, and it "just works". Otherwise, here are
details on how to connect to the desired instance of PostgreSQL.

Your database connection is defined in the **Choose Database Connection**
dialog. The settings in this dialog are to tell CA where to find the PostgreSQL
database server, and how to connect to it, therefore these settings are stored on
the processor / computer you are using, not in the database where the accounting
information is.

**1.4.1Choose Database Dialog**
If this is the first time you are trying to
open CA on a computer it will automatically
show the Choose Database Connection dialog.

If you already have CA open and wish to
connect to a different database (or change
your Look & Feel) select the Menu option:
Company > Choose Database...

**1.4.2Connecting to Who?**
The **Host** field specifies which computer contains the database you want to
connect to.

- If you have only a single processor, or the data (PostgreSQL) is on the
    machine that you're using, entering _localhost_ should work, regardless of
    what type of machine you're on. An alternate to this is **_127.0.0._**
- Regardless of the Word Processor or Computer used, if your machine is
    network enabled, then it should always work to use the IP Address of the
    machine you want to connect to as the Host. On CTS machines this is
    _77.77.77.x_ , with _x_ being the # of the machine hosting the data (1-15 on the
    Steward & Choreboy systems).
- If you're on a **Steward** or **Choreboy** word processor you'll need to use
    **_net1_** , or whatever net # you selected on the machine that is hosting the
    database ( **this is case sensitive, NET1 will not work** ).
- If you're on a networked **CWP 104A** (old model Classic processor):
    ◦ If this is the server machine hosting the database use **_localhost_**
    ◦ For client machines this setting should (usually) say **_server_**. If you have
       your system configured to use a different machine then the server as the

_Chapter 1: Welcome to Classic Accounting!_ **15** CA _User Manual_


```
database host, then use CWPx , with x being a number from 2 through 8
representing the CWP # of the networked machine hosting the database.
```
- If you're using a Windows based Word Processor or Computer then for a
    remote connection use the **IP Address** of the machine you're connecting to.
    In a Windows Workgroup it may also work to use the "name" of the
    computer hosting the database.

After changing the Host you need to click **Refresh** to update the list of
databases available on the specified host machine.

Clicking the **Test** button to will attempt to establish a connection using the set
Host, Database, User Name and Password.

A message will be displayed indicating connection test success or failure. If
Test is successful it should work to click Launch Classic Acct.

Once you have a list of databases to available, select the desired one from the
**Database** list.

Click on the **Launch Classic Acct** button to open the program, connected to
the specified database.

**1.4.3What's your Password?**
In order to connect to PostgreSQL you need to supply a User Name and a
Password. This is **not** same as Logging In / Switching Users (pg 60 ).

The User Name should always be _postgres_ , which is the default user for
PostgreSQL. Classic Accounting is not configured to function otherwise.

All CTS word processors made as of this writing have PostgreSQL configured
to use a standard password: _true_

If you are using CA on computer with Internet access it is advisable to set a
much stronger password than this! Specifying the password is done during the
installation of PostgreSQL, you will be prompted for it.

However, beware that you absolutely must put the password in writing and
store it in a safe location where you can find it if needed. If you forget the
password and Classic Accounting becomes disconnected for some reason it will be
exceedingly difficult to retrieve your data.

```
Specifying A Custom Password
If you set a password other than true when installing PostgreSQL you will
```
_Chapter 1: Welcome to Classic Accounting!_ **16** CA _User Manual_


need to tell Classic Accounting what this password is so it can connect.

Check the **Advanced Options** box at top,
then more fields will become visible where
you can enter the **User** , **Password** and **Port**.

The **Port** option specifies which network
Port PostgreSQL is running on. The standard
installation uses port _5432_ , but it is possible
to change this, and in particular if multiple
versions of PostgreSQL are installed on the
same machine each one needs to use a
different Port.

**1.4.4Adding A New Database**
If you need to add a new database (see
Databases on pg 14 ) you can do so by clicking
the **Add** button and entering a name for the
new database.

This will work only if you have a valid Host, Port, User and Password specified,
there must be a PostgreSQL server running that can be connected to with those
parameters.

The name of the database needs to be all lowercase letters. It should reflect
your business name, or maybe _test_ if it's one you're creating just to play with. You
may not use spaces in the name, use an underscore _ instead to separate multiple
words. You may not include any other punctuation characters like _!',#?_ , etc.

```
This Add action can also be done through Database Utilities (pg 117 ).
```
**1.4.5Other Connection Options**

**Look & Feel**
This enables selecting the color scheme to use in CA. If you use multiple
Databases (pg 14 ) you can set a different Look & Feel for each one, making it
easier to identify them on-screen.

**Always Show on Startup**
If you check this option then this dialog will always pop up when you launch
Classic Accounting. This is useful if you use multiple databases, you can select
which database you want to use during the start-up process.

_Chapter 1: Welcome to Classic Accounting!_ **17** CA _User Manual_


### 1.5 Connection issues.............................................................................................

If you get an error message when
refreshing the database list, or when the
dialog opens, it is likely one of the
following problems. Often the error message will help determine which issue it is
having:

```
✗ Your machine is not connected to the network. Maybe the network settings
have not yet been configured, or there is some issue with wiring or the
network switch.
✗ The target (host) machine is not available. Maybe you misspelled the IP
Address or computer name, or the computer is turned off or otherwise
disconnected from the network.
✗ There is no PostgreSQL server running on the specified host.
✗ PostgreSQL is running but is configured to not accept connections from
other machines. When doing a new networked setup this is very possible,
as the default configuration for most PostgreSQL installers is to accept
connections only from applications running on the same machine. An
installation guide for Windows is available from your dealer.
✗ PostgreSQL is running, but has been installed with a different password
and/or username than the defaults used on CTS machines. See Specifying A
Custom Password on pg 16.
```
_Chapter 1: Welcome to Classic Accounting!_ **18** CA _User Manual_


### 1.6 Connection Profiles...........................................................................................

This feature, found in the Choose
Database Connection dialog, is to make it
easier to use multiple copies of CA, especially
when connecting to different databases.

The combo box at very top contains a list
of all the stored "Profiles".

There is one profile named "default" which
cannot be deleted. It is used if you do not
create any others.

**1.6.1Creating a Profile**

1. Edit the desired parameters for
    connecting to database in Connection Details section.
**2.** Click on **Save As New**
3. Enter a name for your Profile then click **OK**.

The Profile should now be available in the list, if not click **Reload**.

**1.6.2Launching a Profile**

1. Select the desired profile from the List at top. This fills the selected
    Profile's settings in the Connection Details section.
2. Click **Launch Classic Acct** button at bottom right.

**1.6.3Modifying a Profile**

1. Load the profile by selecting it from list at top.
2. Modify the settings as desired in Connection Details section.
3. Click the **Update** button. (Not valid for "default" – clicking Launch will
    update default Profile.)

**1.6.4Launching multiple Profiles at once**
Clicking the **Launch All** button will launch all of the stored user Profiles in
sequence, but not the "default" Profile. This should be useful if you have 2+
copies of CA you wish to open each morning.

_Chapter 1: Welcome to Classic Accounting!_ **19** CA _User Manual_


**1.6.5Other Profile Options**
Beneath the Profile combo box there are buttons for **Reload** (refresh the list of
Profiles), **Rename** (renames the currently selected Profile) and **Delete** (deletes
the currently selected Profile.

```
Rename and Delete are not valid for Profile "default".
```
_Chapter 1: Welcome to Classic Accounting!_ **20** CA _User Manual_


### 1.7 Startup / Version Updates.................................................................................

This section added v2024.1

When you launch Classic Accounting on a new database for the first time it
will run build-in scripts and routines to create the database tables and populate
them with the initial reference and default data.

The first time you launch a newer version of Classic Accounting on an existing
database it will run all required updates to update your existing information to be
compatible with the new version.

In either of these cases it is important that you launch only a single instance of
Classic Accounting, and wait for all the updates to complete and the application
to open before launching additional copies of CA.

It is important that all machines being used on a single database have the
same version of Classic Accounting installed, otherwise your data may become
corrupt because of old version not being compatible with revised database.

_Chapter 1: Welcome to Classic Accounting!_ **21** CA _User Manual_


### 1.8 Classic Accounting Initial Setup Guide............................................................

_Thanks to Aaron Martin of Classic Sales & Service for suggestions on this
page_

It's important that Classic Accounting is set up properly before you start using
it for your business. Each step is explained in detail in a later chapter, and tells
you where to find more information in the manual. You may want to print this
page and use it as a checklist.

When a new database is created CA inserts default settings and basic data to
make it easier to get your accounting system up and running.

1. By default you are logged in as user **guest** , if you try to do something that
    asks for a user log-in then the User Name is **admin** – all lower case – no
    password needed. For more information see Log In As.. on page 125 and
    Securing Classic Accounting on page 59.
2. Enter your Company Info (page 110 ) and in Company Options (page 111 )
    add or edit the various options as needed.
3. In General Ledger set up your GL Accounts – see Accounting Basics, pg 85
    and GL Accounts page 86 & 126. It would be very helpful to have the Chart
    of Accounts that your Tax Accountant is using. That way you could edit the
    GL Accounts to more closely match those.
4. In the Expense menu in Vendors (page 232 ) you will need to edit the tax
    agency – whoever you pay your Sales Tax to – and add the various people
    and companies you buy supplies and materials from. See Import / Export
    Names on page 124 for importing a Vendor list from an Excel spreadsheet.
5. Check and update the various Settings, accessible via The Menu Bar (page
    106 ). Income Settings (page 137 ) and Price Levels (page 130 ) are the most
    important, and should be set correctly before you start using the system.
    New databases only have a _Retail_ Price Level to start with.
6. You need to enter the Items (pg 167 ) that you buy and sell. You'll need to
    edit the existing Sales Tax Item (page 212 ). A **Finance Charge Item** and a
    **Misc Sales** item are already there (see Other Charge Item, page 211 ).
    Read about Inventory vs. Non-Inventory Items on page 169. See Import /
    Export Items (page 121 ) if you have a list Items on a spreadsheet.
7. Enter your Customers (page 263 ). See Import / Export Names on page 124
    for importing a Customer list from an Excel spreadsheet.
8. Enter all **Accounts Receivable** , which are Unpaid Customer Invoice s (page
    277 ).
9. Enter all **Accounts Payable** , which are Unpaid Vendor Bill s (page 250 ) -
    optional.
10.If you're using Inventory Item s (page 191 ) make Inventory Adjustments
    (page 131 ) to adjust the Quantity On Hand of all Inventory Items you have
    on hand when you start using the system.

_Chapter 1: Welcome to Classic Accounting!_ **22** CA _User Manual_


```
11.Enter all outstanding Checks (page 321 ) and Deposit (page 326 ) for each
Bank – Checking and Credit Card – account that you have.
12.Create Journal Entries (page 128 ), and/or Transfer (page 330 ), to correct
the balance of all GL Accounts (page 86 ).
```
_Chapter 1: Welcome to Classic Accounting!_ **23** CA _User Manual_


### 1.9 The Home Screen..............................................................................................

Right now, take a look at the Home screen (or Home Zone) of CA. Each of the
6 big buttons opens another screen that has more buttons, and each of these
screens is labeled as a **Zone**. In this document when we talk about a Zone we are
referring to a screen with action buttons on them, when we talk about the Menu
we are referring to the **Menu Bar** along the top (File, Company, General Ledger,
Items, etc.).

Here is a listing of the **Zones** , and the chapter where each one is explained in
detail.

Item Manager (pg 170 ): Creating, Editing and Manufacturing Items.
Income Zone (pg. 261 ): Tools for tracking incoming money (Customers)
Customers are people you RECEIVE money from.
Expense Zone (pg. 231 ): Tools for tracking outgoing money (Vendors)
Vendors are people you PAY money to.
Banking Zone (pg. 317 ): Manage your Bank accounts (Checks, Deposits)
Payroll Zone (pg. 311 ): Employee and Time Card entry
Reports Zone (pg. 348 ): View and Print reports pertaining to your
business.

_Chapter 1: Welcome to Classic Accounting!_ **24** CA _User Manual_


At the lower right of all Zones (except Home) and most other Forms is a button
labeled **Go Back** (or Close, Exit, Cancel or something similar). Keep clicking Go
Back and you will eventually come back to the **Home** screen. When you open a
different form, it often does not close or remove the one that was open (currently
displayed), it just opens a new one and stacks it on top of any that were previously
open. If you open a different document or entity from one that is already open,
then it may re-use the currently open form. If you open a number of different
forms they will keep stacking on top of each other. Once you start clicking the **Go
Back** buttons, each time you close one form it will make the one underneath it
visible again. Go Back can be activated with the Ctrl+G keyboard shortcut.

If you look at the left end of the black bar immediately below the Menu Bar, it
will tell you which Zone (titled _Menu_ ) or Form you're in, and the name of the
currently logged in user.

Along the top of the screen is the **Menu Bar** , (the words _File_ , _Company_ ,
_General Ledger_ , etc. in the back bar) which enables access to any portion of the
system, including some that have no other point of access (such as the Company
menu). Click on a menu to open it, displaying more choices to click on.

**We will be referring to, and using, the menu quite extensively.** If we say
"select Company Options from the Company menu", that means to click on
Company (the word _Company_ in the black bar along top) then click on _Company
Options_ , which appears after you clicked on _Company_. Selecting a menu option is
often written like this: **Menu > Company > Company Options**.

In The Menu Bar, starting on page 106 , we will go through all the options
available from the Menu Bar.

Application Size: When Classic Accounting is closed it will 'remember' the
position and size where it was located on screen, and re-open to that same
position and size the next time it's opened.

_Chapter 1: Welcome to Classic Accounting!_ **25** CA _User Manual_


### 1.10 General Help on Zones....................................................................................

We will cover some basic now, and for this we will use the **Income Zone**.
Click on the **Income Zone** button on the **Home** screen.

Really Basic Beginner Info: The Rectangles you see on this screen are Buttons.
If you click on a button, something happens. To Click, move your mouse pointer
so it is on top of a button, then push and release the left mouse button.

Notice how the buttons are grouped together, a Large button (with a picture
on it) then some smaller ones underneath it, all linked together with gray lines
along the left.

The large button at the top of each section will always do the same thing as
the smaller button immediately below it.

Each button section gives access to the necessary **forms** for one (sometimes
more) documents.

**1.10.1 New button**
Most groups contain a **New** button that opens the appropriate document form
with a new (blank) document loaded.

Usually the bigger button at the top of the group activates the New _xxx_ option
as well.

_Chapter 1: Welcome to Classic Accounting!_ **26** CA _User Manual_


A few groups have more than one New button, the **Invoices** group (in Income
Zone) has a **New Credit** button to create a Credit Memo (pg 287 ) as well as New
Invoice. Likewise in Expense Zone the Bill / Credit group has buttons for New
Vendor Bill (pg 250 ) as well as Vendor Credit (pg 255 )

**1.10.2 View/Edit button**
This button opens the Document Search Dialog (pg 54 ) showing all the
documents of that type. This dialog allows you to search for a specific document
and to open any document.

**1.10.3 Print (batch) button**
The **Print** button opens a Batch Printing form (page 48 ) for printing that
document type (you can print any single document from within the document's
Add / Edit form).

**A note on Forms:** When you click on **New Estimate** it opens a screen, or
window, where you enter the information required to create an Estimate
document. This type of screen is referred to as a Form throughout this document.
You can think of this as equal to a pre-printed Invoice or other “fill-in-the-blanks”
form that you get from a printer, usually they come in duplicates so you can retain
a copy for yourself. Unlike a pre-printed carbonless form, these forms do not
have the same layout / look as the printed document. A **Dialog** is similar to a
form, but it pops up in its own Frame. The Zones in themselves are a type of
form.

See General Help on Forms on pg 29 for more information.
This same button layout is used on most of the Zones. You will see that it does
vary a bit, Payments and Customers have no Print button, as they do not have
Printable documents, and the Invoice section has additional buttons for Credit
Memo, Finance Charges and Statements.

The Item Manager (pg 170 ) and Reports Zone (pg 348 ) look different from the
other zones.

_Chapter 1: Welcome to Classic Accounting!_ **27** CA _User Manual_


### 1.11 Org: People and Companies............................................................................

Throughout this document, and in CA, you will find references to **Org**. This is
the name of the database table that contains information about all the Customers,
Vendors and Employees (as well as the Company Info). So when we mention **org**
we are usually referring to something that applies to all Customers and Vendors,
and usually to Employees. We can also say that Customers, Vendors and
Employees are "Types of Org".

The author is not sure, but thinks that org is probably short for organization,
although for some businesses most Customers are individuals rather than
organizations.

All of the different types of org share many common features (like a name), but
each one has some that are different from the others.

_Chapter 1: Welcome to Classic Accounting!_ **28** CA _User Manual_


### 1.12 General Help on Forms...................................................................................

Here we will be looking at the **Add / Edit Invoice** form and explaining the
common features that are available throughout CA on many of the different
document forms. For information on the various types of Documents see page 74.

```
In this view we have recalled an Invoice. (See Recalling Documents, pg 77 .)
```
**1.12.1 Name Box**
At the upper left is the Name Combo Box for selecting which Customer you are
Invoicing. In Expense documents this is a Vendor list.

A **Combo Box** is a control with a drop-down arrow that opens a list of options
to select from. A Text Field allows you to type in anything you want, a Combo Box
limits you to entering an item in the list. You cannot create an Invoice for a
Customer that doesn't exist in CA, you must first enter the Customer's name and
information.

To enter a name, click in this box and start typing, which will auto-fill the
name as you type. Once the correct name is displayed, hit the **Tab** key (along the
left side of the keyboard) which will move you to the next field or control. This
will load the Customer's address and settings to the document.

You can also click on the small gray box with the down-pointing arrow at the
right end of this combo-box. It will open a drop-down list of your customers, and
you can use your mouse to navigate the list and click on the one you want.

_Chapter 1: Welcome to Classic Accounting!_ **29** CA _User Manual_


Once you have a large number of customers in the system, it may be more
difficult to find the one you want. The small button with the Magnifying Glass (to
the right of the Combo Box) will open the Name Search Dialog (pg 53 ) with the
cursor focus in the Search field. Start typing any information that will find your
customer, first name, last name, phone number, zip code, etc. Once the correct
name is at top (or click on it to highlight) hit the **Enter** key or click on the **Open**
button to go back to the document form with the selected name entered.

Most forms will also have the small button that opens the Org Info Dialog
(pg 42 ). If you click on this button on a new document, before selecting a
Customer, it will open the form to add a new Customer. (Same with Vendor on
Expense documents.)

**1.12.2 Tax Region**
The **Tax Regions** drop-down along the top, to the right, (only in Income
documents) is used to select which Tax Regions (Sales Tax Item s , page 212 ) are to
be applied to this document. This should be automatic and correct if your Tax
Item, Income Settings and Customer setup is all correct. See Sales Tax, page
378. for more information. Note that the document's Tax Region is used to
calculate the Gross Sales on the Sales Tax Liability report (pg. 365 ).

**1.12.3 Document Date**
The **Date** field is the date of the document. This date will default to the
current date (Today), but it can be changed if desired. If you date a document too
far in the past it may warn you when you save the document, but it is permitted to
do so. This date must be within an existing Transaction Years (page 116 ). See
Date Control (pg 31 ) for usage of the Date fields.

**1.12.4 Document Number (Auto-Generated)**
The **Invoice Number** (or whatever document you're in) you should fill in
ONLY on the very first document of that type that you create. After that, always
leave this field empty, and it will automatically enter the next number for this
document type when you save the document.

The reason CA doesn't fill in the number until you Save the document, instead
of when you open the form to create a new one, is because that caused problems
in multiple-user setups, several Invoices of the same number would sometimes be
created if more then one user was entering Invoices.

If you manually enter or edit the number and attempt to save the document it
will ask if you want to save this as the starting number for future documents.

If you attempt to save with a number that already exists on another document
it will show a dialog with information on the most recent used numbers and the
highest number, and prompt you to change it to an appropriate number.

_Chapter 1: Welcome to Classic Accounting!_ **30** CA _User Manual_


**1.12.5 Next / Previous Doc**
On either side of the document number field there is an arrow button.
Clicking this button will allow you to step through the next (right arrow) or
previous (left arrow) document of this type.

Most document types will step through the next / previous cycle sorted by the
document number, but some (like Vendor Bill) are sorted by the create timestamp.

**1.12.6 Ship To**
The Ship To text field contains the Name / Address that appears on the
document as the Ship To address. This can be edited as desired, and if a
Customer has multiple Ship To addresses entered you can select one of them from
the combo box above the address.

**1.12.7 Date Control**
The Date boxes have a Drop-Down arrow at
the right that you can click to pop up a little
Calendar screen that allows you to select a
desired date.

You can also input dates by typing them, for
example, type _3/15_ to enter March 15 of the
current year. If you want to type in a date that
is not in the current year, include the year:
_3/15/15_.

The Date Control will also accept either a
dash or period as a separator, like _3-15_ or
_3.15.15_.

You can type in the word _today_ to enter Today's Date. Unlike a spreadsheet,
you cannot enter _ASAP_ in a Date Control.

**1.12.8 Document Options fields**
Next you will see a row of Combo Boxes, these contain various settings which
differ for different document types.

**Alert Notes label**
On the document forms there is a **Notes** label that appears when a Customer
is selected that has Notes OR Alert Notes entered (pg 268 ).

- If only Notes are entered then label will be Yellow with Black text. Click on
    label to view notes.
- If only Alert Notes are entered then label will be Red with Black text. Click
    on label to view.
- If both Notes and Alert Notes are entered label will be Red with Green text.
    Click to view Alert Notes and right-click to view Notes.

_Chapter 1: Welcome to Classic Accounting!_ **31** CA _User Manual_


- If no Notes or Alert Notes are entered for the selected Customer the label
    will not be visible.

**Price Level**
The Price Level for this document. It is possible, but not recommended, to
leave this blank. See Price Levels on pg 154 for more information.

```
Also see Changing Price Level on a Document on page 155.
```
**Terms**
The document's Terms represent when the document is due to be paid, and
what discounts are applicable, if any, for prompt payment. There is a single list of
Terms (pg. 111 ) that is used for both Income (Invoice, pg. 277 ) and Expense
(Vendor Bill, pg. 250 ) documents.

```
Via
The Ship Via Methods (pg. 113 ) or method of shipment.
```
**Sales Rep**
Sales Reps can be either an outside Rep that brokered the sale for you, or the
Clerk that entered the Sale in CA. There are some settings in Income Settings
(pg. 137 ) that force this field to be filled in on some documents. Also see Sales
Reps on page 113.

**1.12.9 Notes**
Most documents have a Notes field. This usually prints on the document, and
is used to store information that is shared with the customer. This is a fairly large
text field and will accept up to 5,000 characters of text.

**1.12.10 Memo**
The Memo field is for internal (Company) use, it does not print on any
documents. It will accept up to 1,000 characters of text.

**1.12.11 Created / Modified Label**
Many document forms also have a label above the Notes field (at bottom left of
screen) that shows the **Created date** for the current document. If you hoover
your mouse over the label it will show the **Last Modified date** and the
document's internal ID number as a pop-up text.

Customer and Vendor edit screens, have this label in the top right corner, and
on Item Edit screen it is at bottom left, besides the Active check-box.

**1.12.12 Status Fields**
There are certain display-only labels between the Bill To and Ship To
addresses that show up under certain circumstances.

_Chapter 1: Welcome to Classic Accounting!_ **32** CA _User Manual_


**Transaction Linked**
If this is displayed on the screen, it indicates that
the displayed document is Linked to one or more other document. For example, if
you receive a customer Payment and apply it to an Invoice, then that Invoice will
display **TRANSACTION LINKED**. If you convert a PO to a Vendor Bill, then the
PO will show **TRANSACTION LINKED**.

**Fulfilled**
All Documents have a **Document Status** , this is
generally **OPEN** when the document is first saved,
then changes to some other Status once further actions are taken, such as the
Invoice being paid or the Purchase Order being received. The Document Search
Dialog (pg. 54 ) will only display **OPEN** documents unless you click on the **Show
All** check-box at bottom left of the dialog. This limits the list of documents to only
the ones you are most likely to want to see, and allows the dialog to load the
document list much faster (fewer documents) then it would if it was to show all
documents.

Once a document is Fulfilled, or finalized, then the **FULFILLED** text will show
on the screen. This indicates that all possible actions have taken place, and this
document is now complete and done with. You will not be able to modify much, if
anything, on a Fulfilled document. For Example, if you have an Invoice that has
payments and/or discounts applied to the full amount, then that Invoice is
**FULFILLED**.

A Purchase Order, Estimate or Sales Order becomes **FULFILLED** when all the
Items have been exported to a Vendor Bill or Invoice.

Some documents change to other statuses then **FULFILLED**. An Invoice
becomes **PAID** , a Sales Receipt becomes **DEPOSITED** , an Estimate or Purchase
Order becomes **CLOSED** , and a Check becomes **CLEARED**.

Some documents now have a CLOSED status, which is manually set by the
user. CLOSED indicates the document is not (at least not entirely) FULFILLED,
but is considered completed or canceled.

**Printed**
Many Document forms show a **PRINTED** label if the document has been
Printed. The Printed status is set automatically when you print the document, but
many forms have a Check-box so the 'Printed' status can be set / unset manually if
desired.

Note that clicking a Print button then clicking Cancel on the Print Dialog will
still mark the document as Printed.

Documents will not be marked as PRINTED if you do a Preview instead of a
Print, even if you print from the Preview screen.

Once a document is marked as PRINTED it will no longer show up in the Bulk
Print screen (unless you click Show Printed).

_Chapter 1: Welcome to Classic Accounting!_ **33** CA _User Manual_


**Also, some forms will show other information at the top, close by the
Name Box. These are pretty self-explanatory: Phone, Fax, Balance.**

**1.12.13 Table Control, or Data Table**
In the bottom half of the Invoice form is a Line Items table, where you enter
the Item(s) that your Customer purchased. This is a **Table Control** (also called a
**Data Table** ), and all Table Controls in CA have some features in common.

A table is a bit like a spreadsheet, it has Columns and Rows. The "Cells" are
called fields. Along the top of the table are the Column **Headers** , they tell what
information is in each column.

Special Note: A table will normally "absorb" keyboard input, so if the focus is
on a table control (especially in a cell) most system-wide and application shortcuts
(such as Ctrl+N for new doc, Ctrl+S for save, etc) will not work. Note added 2023.1

```
See Saving The Register To A Spreadsheet (pg 319 ) for a good table trick!
```
**Item Combo Box**
(Also called the **Item Widget** ) Usually the first Column in the Line Items
table, contains the **Item list. This field is a Combo Box that has rather
different behavior.** When you first click on the drop-down there is nothing in the
list!

You will need to type in several letters of the Item that you want, then it will
show all the Items starting with or containing those letters and keep narrowing
down as you type. This functionality is because systems with very large Item lists
are slow in loading and updating when this list shows all available items.

A setting on Item Settings: Other Tab (pg. 134 ) controls how many characters
need to be entered before it starts searching for Items. If your item list is very
large and the search takes too long you may get better performance by increasing
the default value of 2 to 4 or so characters, which causes the first search to return
fewer results.

The search feature accepts multiple words entered in the field (separated by a
space) and breaks these into AND searches. If you type in "5/16 nut" it will find
all the items that have both 5/16 and nut anywhere in the description or item
number. It also searches the VPN. This makes the search extremely powerful and
allows much greater flexibility in the search text. The search is done in multiple
steps in attempt to show the most desirable results on top of the list, therefore
the displayed item list may not be entirely in alphabetical order.

**GL Account Combo Box**
Most combo boxes for selecting GL Accounts (pg 86 ) support text searching
like the Item Widget. This way you can easily find the correct account by it's
name, if you don't know the exact GL Number.

_Chapter 1: Welcome to Classic Accounting!_ **34** CA _User Manual_


```
Multi-Line Text Editor
```
The Description
field for the main
documents has a
pop-up editor
available that can be
used to enter multi-
line text and enter /
view /edit long
descriptions.

This pop-up can
be activated with
either F2 key or
Ctrl+Enter key
combo.

After completing
the edit, the pop-up can be closed the same way, or by clicking on the OK button.
Hitting the Esc key or clicking on the Cancel button will discard any edits you
made and retain text as it was when the editor dialog was opened.

This pop-up editor is available in the Notes and Memo fields of most document
forms as well.

**Column Width / Position / Visibility**
The width of any column can be changed by **dragging** the right edge of the
header of the column you want to resize.

The columns can be re-positioned by dragging and
dropping the entire column header into a new position.
This will not affect any printout, just the screen view

```
At the right end of the Column Headers is Column
```
**Control** selector, a little box that looks like this: It
opens a list that allows you to hide or display columns.
Only the Checked columns will be displayed. You should
check out this list in each document, not all columns are
visible by default. Any table that has this Table Control
Widget will 'remember' if you make any custom settings
to the columns, and keep those settings for you. If you
need to reset everything and start over, use the Clear All
Preferences (page 117 ) option in the Company Menu.
Note: This control has been replaced by the Column
Widget (pg. 36 ) on some tables.

```
At the bottom of this list are additional options:
```
_Chapter 1: Welcome to Classic Accounting!_ **35** CA _User Manual_


**_Horizontal Scroll_**
If this is checked, then the Table will show a Horizontal Scroll Bar and allows
you to stretch columns so the width of all the columns is more then the width of
the visible Table.

**_Pack All Columns_**
Clicking this will reset the width of the currently visible columns to Optimal
(default) Width.

**_Pack Selected Columns_**
Clicking this will reset the width of the currently visible columns to Optimal
(default) Width. OK, whats up? The author was not able to determine any
difference between Pack All Columns and Pack Selected Columns. It's operation
may be just a tad flaky?

**Column Widget**
The legacy Column Width / Position / Visibility control
described above is being phased out and replaced with a
new Column Control device that we'll call the “Column
Widget”.

It is similar, and works almost like the old version. It
can be identified from the previous version by the fact
that the little control at the top right of the table turns

yellow when you hoover your mouse over it.

Clicking on this icon will bring up the column settings
pop-up as shown at right. All the columns are listed, you
can check / un-check them to hide (un-checked) or show
(checked) the column

One notable difference is that this widget usually does
NOT automatically save the column settings for you, you
will need to arrange the columns as you wish then select
the **Save Current Settings** option.

Clicking **Apply Saved Settings** will reset the columns
to how they were saved, and **Clear Saved Settings** will,
well, delete the saved settings and revert column settings
to default. These settings will also be reset (deleted) if
you use the **Clear All Preferences** option from the
**Company** menu.

There is a **Show Horizontal Scrollbar** option, but no “Pack Columns” option
like the other column setting device had.

**Table Row Sorting**
On many tables you can sort the displayed information by clicking on the
Column Header. A little up or down arrow shows that the table is sorted by this

_Chapter 1: Welcome to Classic Accounting!_ **36** CA _User Manual_


column. The sort can be switched from Ascending (A-Z) to Descending (Z-A), the
first click sorts Ascending, clicking again sorts it to Descending.

On tables using the old-style row sorting there is no way to 'unsort' a table
after a sort had been applied, clicking the column header just toggles between
Ascending and Descending order. Now tables using the new style Column Widget
have a 3-state sort, clicking a Column Header will toggle between Ascending,
Descending and Off. These tables will display a little yellow arrow rather then the
black or gray arrows of the default version. Some tables will allow up to 3
different columns to be sorted, you can experiment by sorting one column then
another. This 3-state sorter was first implemented on the Name Search and Doc
Search dialogs.

Some tables can't be sorted in this manner. The Line Items of a document, for
instance, is not sortable at all (it has a Move Row up/down option though).

**Row Controls**
Along the right of a Table control are some more buttons (not all tables have
all of these), they have the following functions:

```
Add Row
```
will add a new empty row to the table, usually immediately below the
currently selected row.

```
Delete Row
```
```
will Delete the currently selected row.
Move Row Up
```
```
will move the currently selected row upward.
```
```
Move Row Down
```
```
will move the currently selected row downward.
Barcode Scan Field
```
is a Barcode Scanner focus field. If you have your Items set up to use
barcodes, click in here then use a Scanner to enter line items. It will turn yellow
when it has the focus. See Barcode Scanning (pg. 297 ) for additional information.

**Notes field**
Most documents have a Notes field. This can be used to enter fairly lengthy
notes and will usually print on the document. Often used for instructions or notes
regarding an Order, both Sales and Purchase. This field has the pop-up Text
Editor feature, use F2 or Ctrl+Enter to activate.

_Chapter 1: Welcome to Classic Accounting!_ **37** CA _User Manual_


**Memo field**
The Memo field is also available on most documents. Unlike Notes the Memo
never shows on the printout except for the Check (see Checking on page 321 ). It
can be used for internal reference, to store a brief note that the Customer will not
see. The Memo field is used to store link info when a document is converted from
one type to another, and is included in the Document Search Dialog (pg 54 ). The
Memo field also utilizes the pop-up editor like Notes.

**1.12.14 Calculator Cells**
Most **Qty** and **Rate** cells can perform math calculations. Instead of being
limited to number only you can enter a formula like "295.95/12" and it will enter
the calculated results in the cell (24.6625 in this case).

This is limited to math operations. It does include rnd(), min(), max(), etc.
functions (see Markup Formulas on pg 162 ). It does not work with Price, Cost
and AvgCost parameters like item price calculations.

In table cells this calculation triggers when you hit the Tab key to move to the
next cell. In the Price field of Item Edit, and other fields that are not in a
table/grid, you will need to hit the Enter key to activate the calculation.

```
1.12.15 Standard Form Buttons
Along the bottom are some buttons that most document forms have.
```
**Drop-Down Buttons**
Some of the buttons have a small Arrow on them, to the right of the text /
image. If you click on or to the right of this arrow it will open a pop-up menu of
additional options. You can also display this pop-up menu by Right-Clicking
anywhere on the button.

**Note:** the 'click area' for triggering the pop-up is not the arrow itself, but the
entire right end of the button. You can see if you're in the pop-up area by the fact
that the arrow icon changes a little, use that as an indicator rather then
attempting to click directly on the tiny little arrow.

The Default action for a button with a drop-down (if it is left-clicked anywhere
except on the arrow, or along the right side of the button) it always the first
option in the list.

```
Line Links
```
This button opens a dialog that allows you to view and go to any linked
documents. Line Links are created when Line Items from a document are
exported to (or imported from) another document (See Converting (Linking)
Documents on pg 78 ). This is useful for tracking down what Invoice a Sales Order

_Chapter 1: Welcome to Classic Accounting!_ **38** CA _User Manual_


was exported to, or what Purchase Order was used to order an Item on a Sales
Order.

Note that the lines are color-coded by document type, and that most lines have
additional information on the help text if you hover your mouse over the line a bit.

Here we launched the dialog from a Sales Order that has only one item on it,
but there are numerous links.

The very top line contains information on this document, the Sales Order.
The next line is an Item line (note the background color is same as the main
dialog's background). This represents a line item on the current document. The
next 3 lines are connected to this Item.

The first (3rd line from top) shows that this line originates from Estimate #
"ESTM 169".

```
The next line shows that a Purchase Order was created for this Item.
The last line shows that this item was placed on an Invoice.
```
We can "follow" any of the links. By right-clicking on the text of a document
line a new tab will open showing that document and its items. These links extend
to the payments received (income side) or made (expense side).

In the next view I right-clicked on the Purchase Order line. Here we can see
that:

1. There is an additional item on this Purchase Order, which originates from
    SO 223

_Chapter 1: Welcome to Classic Accounting!_ **39** CA _User Manual_


2. There are no Vendor Bill or Item Receipt links, so apparently the Items
    haven't been received yet.

We can Open any of the documents for editing by doing a Ctrl+Click on the
document line's text.

```
And by doing a Ctrl+Click on an Item line we can open that Item for editing.
```
```
Print Button
```
Will print the document. When you click here it will open up a print dialog
that allows you to select the printer to use. There are also some other options on
this dialog, such as how many copies to print. Some of the options are not
functional, or have no effect.

**Note** : You cannot print a document before it is saved to the database. A
document is automatically saved before it prints.

Note the drop-down arrow on this button. The pop-up menu will include the
option to **Preview** the document (see page 49 ) rather then printing it. Some
forms will have additional options available, the Invoice's and Sales Order's Print
buttons include options for printing or previewing a **Packing List** (this is the
ONLY way to print a Packing List in CA). _A Print button's default action can be
triggered with the shortcut_ **_Ctrl+P_**_._

```
The pop-up list also includes a PDF <doc type> option for each print, this is a
```
_Chapter 1: Welcome to Classic Accounting!_ **40** CA _User Manual_


shortcut to save the document directly as a PDF. Feature added v2024.1

There is an **<Edit Button Settings>** option at the bottom of the pop-up menu
where you can set the default action that occurs when the print button is clicked.
See Printing Documents on page 46 for details.

```
Save Button
```
The **Save** button also has a drop-down, it's options are **Save & New** (saves the
displayed document to the database and clears the form to create a new one) and
**Save** (saves the displayed document, but keeps it in the form for further viewing /
editing). On the Invoice form there is a **Save & Receive** option in the Save
button drop-down. This will save the Invoice and open the **Receive Payment**
form, pre-loaded with the correct Customer name to receive a payment. On the
Receive Payments form the Save button has a **Save & Print** option, which prints
the Invoice(s) that the payment was applied to.

Once a document is saved, it can be opened and edited by any user on a
networked system.

```
Delete
```
The **Delete** button will delete the current document from the database. If
successful, the document can't be retrieved except by re-entering it.

**_Deleting Documents / Transactions_**
**Special Notice:** Most transactions in CA are _Linked_ or _Daisy-Chained_ to each
other, an Estimate can be linked to a Sales Order which is linked to an Invoice
which is linked to a Payment which is linked to a Deposit which has been
Reconciled. Once a reconcile is done, this whole chain is locked up and can't be
modified or deleted. Well, there is a way – see Changing Cleared Status (pg 319 ).

Any time prior to reconcile you can Delete the last link of the chain to free up
the next link so it can be modified, for example: the Deposit must be deleted so
the Payment can be deleted so the Invoice can be modified (say you happened to
use the wrong Item for a certain line). After you've corrected the Invoice you will
need to re-enter the Payment and Deposit. Ouch! Try to get it right the first time.

For Expense documents the chain goes: Purchase Order > Item Receipt >
Vendor Bill > Bill Pay Check > Reconcile.

```
Open
```
The **Open** button opens a dialog with a Data Table listing all the documents of
that type. It will usually show only the OPEN documents by default. For

_Chapter 1: Welcome to Classic Accounting!_ **41** CA _User Manual_


Customers and Vendors, the Data Table lists Customers or Vendors, rather then
documents.

The 'Open' feature is also available from the Zone screen, for each document
type. It's the button titled **View / Edit**. See View / Edit Customer for example, pg
263.

```
Go Back / Close
```
The **Go Back** button will close the form and switch back to the one that was
previously open. _This button can be activated with the Shortcut_ **_Ctrl+G_**_._

```
Org Info Dialog
```
The **Org Info** button appears to the right of the Customer / Vendor
selection combo box. Clicking this button will open a dialog that contains some
(but not all) of that Customer / Vendor's fields.

This dialog makes it easy to view the most common fields of a Customer or
Vendor without leaving the document form. The most notable exception is the
addresses, which are not displayed on this dialog.

You can edit and save the fields that are displayed, or you can click the Add
and Edit buttons at the bottom left to load this name (or a new one) in the regular
edit form.

This dialog replaces the Add and Edit buttons that were previously available at
this location on the document forms.

If you click this button when there is no name selected in the combo box to the
left of the button it will open form to add a new Customer or Vendor. (v2023.1)

_Chapter 1: Welcome to Classic Accounting!_ **42** CA _User Manual_


**Warning:** If you use the **Add** or **Edit** button on this dialog to open the Add /
Edit Customer form (pg 263 ) you may lose any unsaved changes on the current
document!

**_Save Changes?_**
If you have a document open that has
been modified it will ask if you want to save
your changes or not when you try to exit.

**Yes** will save the document and continue
to the previous form.

**No** will discard the changes made and continue to the previous form.
**Cancel** will stop the Go Back process and allow you to continue editing the
current document.

In this dialog the buttons have **Keyboard Shortcuts**. The underlined letters
indicate the shortcut key to use, hold down the **Alt** key and press / release the
shortcut key to trigger the button, in the shown example **Alt + n** will 'click' the
**No** button. The **Esc** key (top left on keyboard) is nearly always a shortcut for
**Cancel**. This **Esc** key will also cancel editing, if the focus gets locked in a text
field and can't get away, try hitting Esc a few times.

```
You can also 'click' the currently selected button by hitting the Enter key. The
```
_Chapter 1: Welcome to Classic Accounting!_ **43** CA _User Manual_


current selection can be changed by hitting the **Tab** key, and it is indicated by the
dotted line inside the button outline, not necessarily by the darker key.

**1.12.16 Using the Active check boxes**
Once a list item is used in any transaction (document) in the system, it can no
longer be deleted. If an item becomes obsolete (say you have an Airborne
Express Via Method, and you no longer ship Airborne Express) you can set it to
inactive (uncheck the Active option) and it will no longer be available for use on
new documents.

_Chapter 1: Welcome to Classic Accounting!_ **44** CA _User Manual_


### 1.13 Saving Documents...........................................................................................

Perhaps we need to explain just a little bit about how documents are saved. As
explained in Databases on page 14 , CA has 2 parts: The GUI that you see and
interact with, and the Database which saves (remembers) the information that
you enter.

Whenever you click on a **New** <doc type> button it opens a Form with a blank,
unsaved document in it. When you enter information in this document it remains
in existence only on the screen in front of you until you Save it. Once it is saved
you can close the document and it remains in the database's memory. You, or
anyone else connected to that database, can re-open it and it will be just like you
saved it.

You can Edit an existing document and save it again, which will just update the
document. In essence it replaces the old version with the new version you made
when you edited the document.

You can **Discard** changes made to a new or recalled (Editing) document by
clicking the **Go Back** button and choosing to No when it asks if you want to save
your changes. If you discard changes to a new document then it will never have
existed in the database. If you discard changes when Editing a document it will
still have the last saved version of that document in the database.

A **key** point to know and keep in mind : You cannot **Print** any document unless
it has been Saved first. This is due to the fact that CA's printing mechanism
works by extracting information from the Database rather then the GUI (the
screen you see). When you click a **Print** button CA will always save any changes
you made to the document before it prints, or even shows you the Print dialog.

_Chapter 1: Welcome to Classic Accounting!_ **45** CA _User Manual_


### 1.14 Printing Documents........................................................................................

There are 2 ways to print most documents, from the document form or via the
print batch form.

**1.14.1 Printing from a Document**
Within a
Document's form
there is a button for
printing, see Print
Button on page 40.
When you click this
button, it opens a
Print dialog as
shown here. In here
(General tab) you
can select which
Printer to use and
how many copies to
print.

When you click
**Print** in a document
form, it will always
first Save the
document before
printing it.

There is also a
setting **Pages** which allows you to print a certain page or span of pages. This can
be handy with large reports, maybe you only want to print a certain section of the
report. Enter the starting and ending page numbers in the 2 boxes. (This feature
may not work with all printers.)

There are more options available in the **Page Setup** and **Appearance** tabs,
but most of them have no effect.

Click the **Print** button to print the number of copies specified using the
Printer selected.

System bug for **Copy Count**. In the newer CTS Steward / Choreboy operating
system (version 5.5+) there is some system bug present that prevents some
printers from printing more than one copy at a time from any Java application.
There is a partial workaround for this. In Company Options, Per Machine
Settings tab there is a setting for Force Multi-Copy Printing (pg. 115 ). By
checking this option, CA will print multiple copies IF the button's Print Action is
set to **PRINT_NO_DIALOG**. This does not work / has no effect on Batch Printing
form (pg. 48 ).

_Chapter 1: Welcome to Classic Accounting!_ **46** CA _User Manual_


**Print Button Settings**
You can set the default action of the print button by right clicking on it then
selecting **<Edit Button Settings>** , this sets what happens when you click on the
button.

The button's pup-up menu will have alternate colored (print) and plain
(preview) entries for all the different forms that can be printed by that button.
You can edit the Printer Settings for each of the print options (but not the preview
options) by right-clicking on them.

```
Here is a run-down of the various settings available.
```
**_Default Report_**
Sets the report to use. This is
only enabled for the main button
action, not settable in the pop-up
print options. You can **add or
remove custom reports** for this
particular button by using **Add New**
and **Remove** buttons, if you add a
report with the same name as an
existing report it will be replaced.

**_Printer_**
Set the default printer to use.
**_Print Action_**
Specifies the action when the
print button is clicked – With Dialog,
Without Dialog, or Preview. Save To
PDF was added in version 2024.1.

**_Mark Printed_**
Check this if you want this print to mark the document status as Printed.
**_Reset (button)_**
Clears the saved settings and reset to defaults. You can clear all saved print
settings by selecting **Menu > Reports > Clear Print Button Settings** (This will
reset settings in all documents (Invoice, Sales Order, etc).

```
Cancel (button)
Exit without saving the displayed settings.
```
**_Save & Close (button)_**
Saves the displayed information and closes dialog
Every print button on the different screens, (Invoice, Sales Order, etc) has its
own settings, and the settings are saved for the current machine only, does not
affect networked machines.

_Chapter 1: Welcome to Classic Accounting!_ **47** CA _User Manual_


**Also Print**
If you want to always print a Packing List or other secondary document each
time you print the main document you can select a secondary document to print
in this section.

These settings are similar to the main document settings, you can choose the
document to print (Also Print combo box), the **Qty** , **Printer** and **Print Action**.

If you don't always want to print the secondary document, but want the option
to do so you can set the Print Action to PRINT_WITH_DIALOG. That way when
the printer selection dialog appears you can choose to either Print or Cancel it.

**1.14.2 Batch Printing form**
If you view the buttons for a particular Document Type within a Zone, there is
usually a **Print** button included (unless it's not a printable document). Clicking
on this button will open the **Batch Printing** form, which allows you to print a lot
of documents at once.

All printable Documents have a "Printed" flag (internal setting) that sets to
_True_ once that document has been printed. If you create new documents and
don't print them right away, the "Printed" flag will be _False_ , and those (unprinted)
documents are available for Batch Printing.

A good
example is the
FC Invoices
created when
you Assess
Finance
Charges (page
302 ). These
Invoices are
auto-generated,
and the easiest
way to print
them is using
the Invoice
Batch Printing
form.

In the
Invoice Batch
Printing form
shown here,
we've been creating some test documents but we haven't Printed any of them.

In the default view only unprinted documents are shown, and all documents
are checked to be printed. You can unselect any or all of the documents ( **Print**
column) and print only the ones you want (the ones that have Print checked).

_Chapter 1: Welcome to Classic Accounting!_ **48** CA _User Manual_


The **Printed** column (far right) shows if this document has been previously
printed or not. The leftmost column, **Print** , is the only column of this table that
can be modified.

There is a **Status** filter at the upper right that allows you to show only
documents that have a certain Status, such as _FULFILLED_.

There is a **Show Printed** check-box at lower right that will display ALL
documents of this type, which allows you to reprint a batch of documents.
**Warning** : Once you have a lot of saved documents, it can take a long time to load
if you click here. Unless you really want to print a lot of old documents it's
probably faster to open the individual documents and print them.

Click the **Print Batch** button to open the same **Print** dialog shown on
previous page.

**Warning:** Clicking the **Cancel** button on the **Print** dialog will set the
document's "Printed" flag to _True_ , even though it doesn't print them. Sometimes
this is desirable (for Checks), other times it is not.

**1.14.3 Print Preview**
Nearly all Print buttons have a Drop-Down with a Preview option. The small
down-pointing arrow to the right of the Printer picture will change size slightly
when you hover your mouse pointer over it. Clicking (left button) at that moment
will open a list that gives you the option of printing or Previewing. Clicking on
preview will open the document on screen in a Preview Window. This window has
some controls along the top of the frame.

**Save as PDF**
The first button on the
left is the **Save** button.
Clicking here will open a
file browser that allows
you to select a location and a name for your file, as well as the file format.

This dialog will open up in the Current Directory, which in a Classic Word
Processor is the _Home_ folder ( _/home/classic_ or _/home/default_ ). You can open any
folder listed in here by double-clicking it, to go to the location that you want to
save your file in.

_Hint: Double-click on the blue folder, rather then its name (the text). Clicking on the text
tends to select the text for editing (renaming) instead of opening the folder._

_Chapter 1: Welcome to Classic Accounting!_ **49** CA _User Manual_


You can create a new folder using the little button along the top (3rd from right).

In the **File Name** field type the name of the file you are saving, where we've
entered _MyDocument.pdf_

In **Files of
Type** list select
the format that
you want to save
the file in. There
are quite a few
options here, the
most used one
being PDF. **PDF**
is a _Portable
Document
Format_ file which
can be read and
printed by most
systems.

**Warning** :
The default **Files
of Type** selection
is not usable.
There is no program on the Classic Word Processor and most other machines that
can read Jasper Reports. Well, why is it there??? When you open a Preview, you
are looking at a Jasper Report, but there is currently no viewer build into CA that
can open a saved _.jrprint_ file! **Always change this to PDF (or other) before
clicking the Save button**.

**Warning** : During testing, the Author crashed OpenOffice by attempting to
open a _.docx_ (Microsoft Word) file created by this **Save** dialog. All the available
formats were tested, the one that is really worthwhile is PDF. The _.html_ (Hyper
Text Markup Language) format is readable if you have a Web Browser, and the
_.xls_ (Microsoft Excel) format provides pretty good results (some reports are
optimized to be saved as Excel files). There is an ODT option available, which is
the _Open Document Format_ Text File that is used by OpenOffice and LibreOffice.
ODT results are often fairly accurate, usually better then any other format except
PDF. A lot of the other formats are unreadable or totally useless.

Sometimes it is desirable to have a better quality file then the PDF that is
created by a **Save As** or **Export** process (this applies to OpenOffice as well). An
alternative is using a **PDF Printer**. If you're using a Classic Word Processor or
another Linux system with a CUPS printer setup, then the PDF Printer is build in,
you may need to have your dealer or administrator help you set it up. If you're
using a Windows system, very good results can be obtained using a free software
called _PDF24_ , or a poplar software called _CutePDF_. A **PDF Printer** adds a
printer to your system's list of printers, then when you print a file using that
printer, it creates a _<xxx>.pdf_ file in your system instead of outputting to a
physical printer. In the Classic system it creates a file inside a folder named _PDF_

_Chapter 1: Welcome to Classic Accounting!_ **50** CA _User Manual_


in your Home folder. Using a PDF Printer tends to create a file that looks more
like one that is printed with a real printer, and often has better quality graphics
then a file created with a Save/Export As PDF.

**Note:** Another way to save a document as a PDF is to use the PDF feature of
the Print Button's pop-up menu (pg 40 ). Reports from the Reports Zone (pg 348 )
can be saved to PDF via the Export button on the Report Prompts dialog..

The 2nd button from left on a Preview screen is **Print**. This opens a Print
dialog, same as clicking a Print button. When using the Preview on large reports,
sometimes you only want to print a few pages of it, then the **Pages** option on the
print dialog can be used.

The 3rd button is **Refresh** , but it is not active, does nothing.
There is a field along the top that shows the Page Number of the current page,
use it to determine the start / end pages to print. You can also enter a desired
page # in here and hit Enter to go to that page.

The remaining controls are for navigating and scaling the image. Just click
each one and see what happens!

**1.14.4 Label Printing**
CA has the ability to print address labels directly from CA using a Dymo
LabelWriter or similar thermal roll label printer.

On any form that you find a or button used as the label above

the Bill To (or Ship To) address block you can click on the right edge of the button
(the drop-down arrow) for a list of Labels available to print, or just click on the
button to print the label specified by the button's **Edit Button Settings** (see
prior section).

Special Note: The label buttons have the same type of pop-up menu and
options as the regular print button, but they are different in that there are only 2
different setting files for all the label buttons, all the **Bill To** Address buttons
share one setting and all the **Ship To** Address buttons share another. These
shared settings are somewhat problematic, if you save settings for the Label
buttons, particularly when adding or removing prints, you may need to close and
re-open CA for the settings to properly load on all buttons.

**Warning** : If you have a Classic / Steward / Choreboy word processor, or a
Linux computer, be careful what kind of label printer you get. The Dymo
LabelWriter 450 series works very well with these machines, but they have been
discontinued and replaced with the LabelWriter 550 series. As of this writing
there are no Linux drivers available for the 550 series, so they will not function.
There are other label printers available, contact your dealer. (v2023.1)

_Chapter 1: Welcome to Classic Accounting!_ **51** CA _User Manual_


### 1.15 Search Dialogs................................................................................................

The **View / Edit** and Open buttons open a Search Dialog for finding the
Document or Name you want. See General Help on Forms (pg. 29 ) for the
difference between a Form and a Dialog, and Types of Documents (pg 75 ) for a
list of the various documents.

There are 2 different Search Dialogs you will be using frequently, the Search
Names (Customers, etc.) dialog and the Search Documents dialog (Invoices, Sales
Orders, Checks, etc., etc.).

**1.15.1 General Use**
What you do is scroll or search through the list, then when you find the one
you want you select it by clicking on it. The selected row will have a darker, or
different, color. Once a row is selected you can either double-click on that row,
hit the Enter key, or click the **Open** button at bottom to open the selected line in
the appropriate screen for editing.

You can choose which columns to display. Beware that the search dialogs use
the new style Column Widget (pg 36 ) which will not auto-save, you need to

click the **Save Current Settings** option if you want the dialog to retains the
Column Settings. Click the Column Widget to show all available columns.

The search tables also use the revised Row Sorter, see Table Row Sorting on
page 36. The **Name** column shows the First / Mid / Last Name, and can be
searched in the Find box.

**1.15.2 Searching a list**
When the dialog opens, the focus (cursor) will be in the **Search For** field at
the upper left. To search for a customer, just start typing the name. As you type,
it will **Filter** the list to show only customers that have text matching what you
typed. When you can see the Customer or Document you want, you can press the
Down Arrow key until the desired row is selected. Once selected, hit the Enter
key to open that customer for editing. Clicking the Search button is not required
anymore, unless you are entering less then 3 characters in the search field. In
earlier versions it did not auto-filter when typing.

**Search Text** : You can search for just about anything, according to the type of
list you have including document number, date ( _2/15_ , etc.), name, phone number,
address, city, etc. The search text is NOT case sensitive, typing _joe_ will find _JOE_
and _Joe_ as well as _joe_. You don't need to type the starting characters, typing
_miller_ will find all the _Millers_ , as well as everyone that has a _Millersburg_ address!

**Special Character** : This is a handy feature if you can remember it: The %
character can be used as a placeholder for any unknown character(s). Example:
typing "jo%mil" will find "John Miller", "Jonathan R Miller", "Jose Amilo", etc., it
searches for the characters "jo", followed by the characters "mil" somewhere later
in the same field. Using _ (underscore) will match any SINGLE character instead.

_Chapter 1: Welcome to Classic Accounting!_ **52** CA _User Manual_


Clicking the **Clear** button will clear the text from both search boxes and set
the focus to the first search text box.

**1.15.3 Name Search Dialog**
For the Name Search dialog, there are 3 different uses of this dialog, for
Customers, Vendors and Employees.

The Name search dialogs also have **Activate** and **Inactivate** buttons, which
will change the Active status of the currently selected name, an **Add** button for
creating a new Customer / Vendor, and a **Delete** button for deleting the currently
selected name.

```
On Name Search dialog there is a single search text box where you can type in
```
_Chapter 1: Welcome to Classic Accounting!_ **53** CA _User Manual_


multiple words or search phrases to filter the list.

The Name search dialogs have a **Show Inactive** check-box which will display
the Names that have been set to Inactive.

**Search For:**
The Search text box will filter your name list will find matches in any of the
following:

✔ Name + Name Extension
✔ Company Name
✔ Bill To Address
✔ Contact
✔ Alt Contact
✔ Phone
✔ Alt Phone
✔ Fax
✔ Email
✔ Check Name (valid for Vendor only)
✔ Person (First + Mid + Last Name)
✔ Account #
➔ **Account No.** : If you use Account Numbers for your Customers or
Vendors you can search by Account Number by using the # character
then the Account Number. This is an Exact Match search, entering **#100**
will find only Account Number 100, not number 1001 or 3100, etc.
This dialog has option to show Notes and Alert Notes columns, which are not
used in the search.

**1.15.4 Document Search Dialog**
Nearly all the different document types have this search dialog available to
make it easy to find the desired document.

**Search For:**
Type text in this box to filter (find) matching documents. Valid text to search
includes

```
✔ Doc Number
✔ Org (Customer or Vendor)
✔ Memo
✔ PO / Ref
✔ Total
```
_Chapter 1: Welcome to Classic Accounting!_ **54** CA _User Manual_


```
✔ Date (must enter in MM/DD/YYYY format)
✔ Bill To name/address
✔ Ship To name/address
✔ Rep Name
```
**Show All:**
By default only OPEN documents are shown in the list. At the bottom of a the
dialog is a Show All check-box that will updated the display to show all
documents.

**New button**
This creates a new document of the type you're searching. Note that this
button can't be used to create Credit Memos or Vendor Credits, as they're a
secondary trans type of Customer Invoice and Vendor Bill.

**Options for customizing Search Dialog:**
In Per Machine Settings (pg 114 ) tab of Company Options dialog there are
several settings that allow customizing the Doc Search Dialog.

**_AND:_**
If Show Dual Search Boxes for Documents is checked then the **AND** label
and an additional text box are displayed in the search dialog. This enables

_Chapter 1: Welcome to Classic Accounting!_ **55** CA _User Manual_


creating a more complex filter, such as searching by the Customer (or Vendor)
Name AND the PO / Ref #

**_Show Docs From:_**
This date field limits the list to only documents created on or since the
selected date. By default this date is 30 days from today (when dialog is first
opened). There are options in Per Machine Settings to set a specific default date
value, or to have it clear (shows all documents). Unless you have a reason to do
otherwise the "Use No Default Date" option is recommended.

**_Shared Settings_**
If the setting **Save Trans Search Columns for
Each Document Type** option is un-checked then all
document search dialogs will share the same Column
Settings (width, position, visibility), or if checked then
each document type (Invoice, SO, PO, etc) will have
separate settings.

The doc search dialog has Column Width / Position /
Visibility control (pg. 35 ) and Table Row Sorting (pg. 36 )
to customize the display and sort results. After adjusting
columns you need to click on the **Save Current Settings**
button.

**Checks Search**
When using this dialog to find Checks or Deposit an
additional filter appears at top right (image below) that
allows you to select a banking account and have the dialog
show only checks written from a given account.

_Chapter 1: Welcome to Classic Accounting!_ **56** CA _User Manual_


### 1.16 Other General Tips..........................................................................................

**1.16.1 Multi-Selection**
Some controls in CA allow multi-selection, such as in the File Picker dialog
that is used by the Report Manager (pg 349 ). This is not unique to CA, but used
in other applications as well.

- To select the desired elements (such as a file in the File Picker) one at a
    time, select the first element then hold down the **Ctrl** key while clicking on
    each additional elements you want.
- To select a block of elements click on the first element you want included,
    then hold down the **Shift** key and select the last element in the block – all
    the elements in between will become selected.
- _To select all elements in the list, use the Select All shortcut: hold down_ **_Crtl_**
    _and hit the_ **_a_** _key_

**1.16.2 Inserting Special Characters**
Sometimes it is desirable or necessary to use special characters in your text
that are not available on a standard keyboard. By using the **Special Characters**
dialog you can select from some of the more common characters.

Select the **Insert Character** option from the **Edit** menu. The cursor focus
needs to be in a text field for this to work. You can also open this dialog with the

_Chapter 1: Welcome to Classic Accounting!_ **57** CA _User Manual_


F6 key.

Double-click on the character you want to insert it at the current text cursor
location. Along the bottom a list of the most recently used characters are
displayed, this list will clear when CA is closed.

**1.16.3 Form Stacking**
It might be helpful if some explanation was made on how opening / closing the
document Forms in CA works (see General Help on Forms, pg 29 ). We are being
creative here and using some terms / words that are not totally correct in the
technical sense, but might be help the non-programmer understand why some
things happen in CA the way they do.

- Each different "view" (screen) you can see in CA we call a **Form** , (we've
    been doing so throughout this manual). Visualize each one (Invoice,
    Purchase Order, etc.) as a pre-printed fill-in-the-blanks carbonless form. In
    CA we are using 2 different "Stacks" (as in a stack of papers) of these forms,
    the **Working Stack** and the **Discard Stack**.
- The application creates a single Form for every different type of document /
    window you open. All documents of one type share the same Form, CA just
    "erases" the previous document and fills in the next one. A few Documents
    share the same Form, like Invoice and Credit Memo.
- The first time you open an Invoice, it will create the blank form and load the
    Invoice (a new one, or the one you choose to recall) onto the form for you to
    work with. The Form is then placed on top of the Working Stack, and is
    what you see on-screen.
- If you click the **Go Back** button to exit the Form it is placed on the Discard
    Stack. _Whichever form was previously on top of the Working Stack now_
    _becomes visible again_ (probably the Income Zone form). You always see the
    topmost form on the Working Stack!
- However, if you use the Menu Bar or a Shortcut to open a different Form
    (say we used Ctrl+Shift+T to open a new Purchase Order), the Invoice
    Form remains on the Working Stack and the new Purchase Order Form
    (with a blank PO loaded) is placed on top of it.
- The next time you open an Invoice it will use the existing Form, but clear
    the previously loaded Invoice and load the new (or recalled) one. It will
    take Form out of whichever stack it was on, and place it on top of the
    Working Stack.
- Summary: If you use the Menu Bar and/or Shortcuts to move around CA,
    your Working stack will build up. By using Go Back and navigating with the
    buttons in the Zones themselves, most Forms will end up on the Discard
    stack. The author prefers the latter method, but there is no known
    performance benefit or penalty either way.

_Chapter 1: Welcome to Classic Accounting!_ **58** CA _User Manual_


## Chapter 2: Startup Considerations..........................................................

This chapter deals with some of the actions you may want to take early in your
accounting setup, such as setting up User roles and importing Items and/or
Names (Customers and Vendors).

### 2.1 Securing Classic Accounting............................................................................

*This chapter and a lot of the Security Zones, plus some new features, were
added in v2022.1 – v2024.1*

If you are trying to do something and Classic Accounting asks you to Log In, or
says you don't have permission to do this, then you need to log in as a different
User that has the necessary Security Zone clearance to do what you're attempting
to do.

If you never modified the Users or passwords you should be able to log in as user
**_admin_** by entering _admin_ as the User Name and leaving the Password box empty.

What your concerns are with **Security** for Classic Accounting will depend on
several factors.

- If you (or one person) are the only user of CA then you will probably not
    wish to deal with User log-in, etc - you just want to get your accounting
    done. This is the default setup when creating a new database.
- If you have multiple employees using CA you may wish to create a User for
    each employee and limit the areas of CA that each User can access.
- If you wish to store Credit Card numbers in CA then you will need to create
    one or more User that has permission for Credit Cards. The build-in _guest_
    and _admin_ users are not allowed to enter Credit Card data, as law requires
    that CA keeps record of who adds, edits and accesses each Credit Card
    number.

In CA security is controlled by **Users** (also known as a "Log-In" or "Log-In Role")
and **Security Zones**.

Each Security Zone covers a certain area or action in CA, the current User can
only perform actions in Zones that are enabled for that User.

Each User can be assigned a password, requiring the password to be entered to
Log In as that User.

There are 2 build-in users that cannot be deleted, and have special functions.

- **_guest_** User is automatically logged in when CA is opened. It is not possible
    to assign a password to _guest_. It is possible to remove all Security Zone
    permissions from _guest_ , which renders it useless and forces logging in as a
    different user to do anything. It is also possible to allow _guest_ permission

_Chapter 2: Startup Considerations_ **59** CA _User Manual_


```
for all Security Zones, which makes it un-necessary to ever log in as a
different user (unless you store Credit Cards).
```
- **_admin_** User always has permission for all Security Zones except Credit
    Cards, but can be assigned a password. If you wish to deny certain people
    access to certain Security Zones then it is important that you assign a
    password to the _admin_ User or they can log in as _admin_ and access
    anything.

If adding Users to CA in order to limit what each one can do, it is important that
those Users do not have permission for the **_Users_** Security Zone, or they can edit
their own permissions or set up a new User.

**2.1.1Logging In / Switching Users**

There is always one single User logged in at any given time. Switching users is
done via the **Log-In Dialog** , which can be accessed with the keyboard shortcut
**Ctrl+L** , or via the Menu option: **Company > Log In As...**

In the top field you enter your User Name (see next section) and Password (if one
is assigned, otherwise leave Password empty).

**2.1.2Adding a new User**

Open the main Users list (dialog) with Menu > Company > Users.

This dialog shows a list of all the Users in CA. Note that there is a **Name** and also
a **User ID**.

- The **Name** field is what displays on Classic Accounting as the current User.
- The **User ID** is the what is entered to Log In.

_Chapter 2: Startup Considerations_ **60** CA _User Manual_


Like a lot of other lists in CA, once a User is no longer needed in the system it can
be made In-Active. Click the **Show Inactive** option at the bottom left to show
Users that are not active.

Most of the options and Security Zones are self-explanatory, but a few might not
be. This dialog view has been expanded so you can see all the **Security Zones**.

_Chapter 2: Startup Considerations_ **61** CA _User Manual_


- **Auto Log Off To Guest** option. If this is checked the User will
    automatically be logged off and the **_guest_** user logged in if no transactions
    are entered or modified in CA after 10 minutes.
- **Time Before Logoff (Min)** sets the number of minuets of no activity*
    before this user is logged out and the guest user logged in. *Activity is
    normally saving a document or opening a form / dialog, there are some actions that do not
    reset the logoff timer. This setting added v2024.1
- **Allow Credit Cards** option. If this is checked then the User is allowed to
    enter and edit Credit Card numbers (see Cards (button) on page 267 ).
    These actions are recorded in CA, including the current user id, and can be
    retrieved by CTS if needed for audit purposes, etc.
- Password / Verification. In order to set a password for a User you need to
    enter the same password in each of these 2 fields. Passwords are case-
    sensitive!
- **Items** vs. **Item Manager** Security Zones. If a User has permission for Item
    Manager, but not Items, then that User can view the Item list via Item
    Manager (pg 170 ), but is not allowed to add or edit Items.
- **Sales Receipt** Security Zone. If a User has permission for only this Zone
    and none others then the User can use the Sales Receipt form (pg 294 ), but
    nothing else. This is for cashiers at a store, allowing them to make sales but
    not access anything else.
- Reports - see Reports Zone (pg 348 ) - each individual report declares which
    (if any) Security Zone it requires. Some require Reports, others Admin,
    other Item, etc.

When you attempt to do an
action that is not permitted for
the currently logged in user it will
display a **Not Authorized** dialog.
Clicking the **Log In** button on
this dialog will display the Login
dialog, which enables you to
enter the appropriate username
and password to access this
action in CA.

_Chapter 2: Startup Considerations_ **62** CA _User Manual_


### 2.2 Importing / Exporting / Updating Items...........................................................

Currently there are 2 different forms in CA that allow you to import items from
a spreadsheet into CA (and export your Items to a spreadsheet). The original
form is available through the Admin Tasks screen (pg 117 ), it is still maintained
because it contains a few features not yet available in the new form. See
Importing Items from other Documents on pg 286 for info, but try to use the new
form explained here when possible, as this old form will eventually be removed.

The newer form is called Update Items by Import and is an attempt to address
the many request for an easier way to edit items and update prices. It is accessed
via the Items Menu (pg 130 ).

```
We are expecting this form will get additional functionality in the future.
```
**2.2.1File to Import / Export**
Regardless if you want to Export, Import or Update your Item list, you always
need to enter the Excel (.xls) file that you wish to use.

- For Importing and Updating you need to select an existing .xls file with your
    Item List.

_Chapter 2: Startup Considerations_ **63** CA _User Manual_


- For Exporting your Item list you want to enter a file name that does not
    exist.
    ◦ Click on the Browse button, navigate to the folder you want to save the
       file in, then in the **File Name** field at bottom type in a the name for the
       new file. Click **Save** to enter the file path in the file path field on the
       screen.
    ◦ Use only letters and numbers for the file name, do not use characters
       such as # or ', as it may cause the operation to fail.
- The file needs to be in the correct Excel format, you cannot import a native
    ODS (OpenOffice /
    LibreOffice) spreadsheet.
    ◦ If your Item list is in
       a .ods (or other)
       spreadsheet and you
       have LibreOffice
       installed on your
       computer you can
       transform it. Click on
       **Menu > File > Save**
       **As** , then select
       **Microsoft Excel 97-**
       **2003 (.xls)** from the
       **File type** list at bottom. Enter a valid **File name** then click **Save**.

**2.2.2Import Limitations**
There are some limitations in the software CA uses to read the spreadsheet
with the item list.

- Currently only .xls files are supported, which is is Microsoft Excel 97-2003
    file format.
- Only the first 65,000 lines on a spreadsheet will be read and imported, even
    if the sheet contains more lines.
- It is recommended that you limit Item Import files to a maximum of around
    30,000 Items per file. If you have much more than this it's probably faster if
    you split it into multiple files and import them one at a time.

**2.2.3Columns and CA Fields**
On the Spreadsheet file each Column represents one "field" in CA. The
spreadsheet columns are defined by the **Headers** , or the field names / column

_Chapter 2: Startup Considerations_ **64** CA _User Manual_


labels in Row 1 of the spreadsheet.

The spelling and capitalization of the column header needs to be exactly right
in order to work.

**2.2.4Available Fields**
In order to know what fields (spreadsheet columns) are available to import you
should manually add a few items to the system (if there are none yet) and export
them. View the spreadsheet and see what columns are available, most of them
are valid to Import as well as Export.

- You cannot import Inventory Items unless the Enable Inventory Items option
    is enabled (pg 133 ).
- If you are importing Inventory Items and you want to have the correct Qty
    On Hand imported you will need to enter that number in a column named
    "ACTUAL QOH". (Name the column containing your Inventory Count as
    **ACTUAL QOH** rather then just **QOH** .)
- It is not possible to import or export multiple Units, CA will only import /
    export the Main Unit.
- Not all fields in CA are available to import or export.

_Chapter 2: Startup Considerations_ **65** CA _User Manual_


**2.2.5Adjusting Inventory QOH
Warning:** Before doing any Inventory Adjustments confirm that the Invalid
Inventory report (pg 367 ) is not showing any items. If that report is showing
items showing with invalid QOH you should run the Reset Inventory Qty On Hand
utility first (pg 135 ).

**Warning** : The system will NOT adjust your QOH +/- the amount shown on
spreadsheet, instead it will calculate and make an adjustment that sets the Item's
QOH to be equal to the value in the **ACTUAL QOH** column (not the **QOH** column)
on the spreadsheet AS OF the date you enter in the **Adjust As Of** field.

**_Update Inventory QOH_**
If you are importing Inventory Items you need to check this option if you want
the system to create Inventory Adjustments (pg 131 ) to set the newly imported
Item's QOH to that shown in the "ACTUAL QOH" column.

You need to have Inventory Items option enabled in order to import new
Inventory Items. See Enable Inventory Items on pg 133.

**_Adjust As Of_**
If you are setting up a new Item list for CA the **Adjust As Of** date should be
the current date.

If you are updating the QOH of your existing Items using an Inventory Count
from a certain day, then the **Adjust As Of** date should be the date the Inventory
Count was done. (Transactions in CA since that date will taken in account when
the Inventory Adjustment is created.)

_Chapter 2: Startup Considerations_ **66** CA _User Manual_

```
Example of Item list exported from CA, as viewed in LibreOffice 5
```

### 2.3 Exporting Items.................................................................................................

1. Enter a file path to export to using the **Browse** button at top. See File to
    Import / Export.
2. Select any filters desired from the **Export Options** section.
3. Click on the **Export** button.
    This should create a file in your system with the name you specified.

_Chapter 2: Startup Considerations_ **67** CA _User Manual_


### 2.4 Importing New Items........................................................................................

When Importing Items from a spreadsheet CA will use the New Item Defaults
in Item Settings (pg 132 ) for filling in the GL Accounts (Sales Account, Purchase
Account, etc) and the Update Cost from Purchases option.

```
Warning : Read Import Limitations!
```
1. Confirm that your spreadsheet of items has the correct headers - it will not
    import properly otherwise. See Available Fields.
2. Confirm that your spreadsheet is of correct file type - it needs to be an 97-
    2003 Excel file format (end with .xls), see File to Import / Export.
3. Choose the file to be imported using the **Browse** button at top.
4. Check the **Import New Items** option.
5. If you are importing Inventory Items and wish to have the QOH adjusted
    then check the **Update Inventory Qty On Hand** option and fill in the
    Adjustment Date and Adjustment Account. See Adjusting Inventory QOH.
6. Click the **Import** button.

**Things to note:**

- If the VENDOR column contains a name that is not in the CA Vendors list
    (pg 232 ) it will create a new Vendor with this name.
- I the ITEM GROUP column contains a value that is not in CA Inventory
    Groups list (pg 130 ) it will create a new one.

_Chapter 2: Startup Considerations_ **68** CA _User Manual_


### 2.5 Updating Items..................................................................................................

With the Update Items By Import feature you can update the Cost, Price, Sales
Description, QOH, etc. of your existing items.

```
Warning : Read Import Limitations!
```
1. Confirm that your spreadsheet of items has the correct headers - it will not
    import properly otherwise. See Available Fields.
2. Confirm that your spreadsheet is of correct file type - it needs to be an 97-
    2003 Excel file format (end with .xls). See File to Import / Export.
3. Choose the file to be updated using the **Browse** button at top.
4. Check the **Update Existing Items** option.
    4.1.If you are importing a list that you exported from this same database
       then you should check the **Match ITEM ID** option as well. This will
       ensure that the correct item is updated. _If you check this option when_
       _importing a list that was exported from a different CA database it will probably_
       _make a real mess of your item list_.
    4.2.If you are importing from a manufacture's list that includes new items
       that are not in your system yet you can check the **Import New Items**
       option as well, and it will add any new items (where the Item Number
       does not exist in your system) to your Item list in CA.
5. If you are have Inventory Items and wish to have the QOH adjusted then
    check the **Update Inventory Qty On Hand** option and fill in the
    Adjustment Date and Adjustment Account. See Adjusting Inventory QOH.
6. Click the **Import** button.

_Chapter 2: Startup Considerations_ **69** CA _User Manual_


### 2.6 Import / Export Addresses................................................................................

If you have a spreadsheet with a list of Customers or Vendors you can import
that list into Classic Accounting. This can save a lot of time during initial setup,
but be careful that you don't end up cluttering CA with a lot of names that you'll
never use.

This feature is accessed via Menu > Company > Admin Tasks > Import /
Export Addresses.

You can Export your list to a spreadsheet to use for other purposes, such as
sending to a printer for mailing list purposes.

```
This feature can import / export Employees as well as Customers and Vendors.
```
Most of the same Import Limitations noted in the import Items section (pg 64 )
also apply here.

See the File to Import / Export section on page 63 for information on the file
format requirements.

```
At bottom of form are listed all the required fields for importing names.
```
_Chapter 2: Startup Considerations_ **70** CA _User Manual_


**2.6.1Create Template**
When you want to import a Customer / Vendor list you need to know what
fields are available to import and what the header name needs to be (see
Available Fields on pg 65 ).

If you click on the **Create Template** button it will create an empty
spreadsheet of the selected Address Type. You need to fill in the name of the file
to be created at top, you generally don't want to replace an existing file so enter a
new (non-existent) file name for this.

In this template all the Red header names are required fields - your import file
must include these columns even if they are empty. All the other (black) header
names are optional columns.

_Chapter 2: Startup Considerations_ **71** CA _User Manual_


### 2.7 Exporting Names...............................................................................................

Pretty straight-forward, but read section 2.6 first.

1. Enter a file path to export to using the **Browse** button at top. See File to
    Import / Export.
2. Select the Address Type and any desired filters from the **Export** section at
    right.
3. Click on the **Export** button.

_Chapter 2: Startup Considerations_ **72** CA _User Manual_


### 2.8 Importing Names..............................................................................................

When importing Names / Addresses you need to select or confirm a number of
options in **Import** section on the Import Addresses screen first.

If you have a list of customers where some of them should have different Price
Level, Terms, etc. then others you should split the list into a separate spreadsheet
file for each different combination of settings. Otherwise you'll need to edit each
individual customer in CA afterward to get everything correct.

1. Choose what type of name list to import in the **Address Type** list.
2. If importing Customers confirm that the desired **Price Level** is selected.
3. Select / confirm the correct **Terms** (not used for Employee).
4. Confirm the Def. Credit Limit Is correct (see pg 267 ).
5. If importing Customers then check-mark all taxes in the **Exempt Taxes** list
    that you want to be Exempt (not charge when invoiced).
6. Click the **Import** button.

_Chapter 2: Startup Considerations_ **73** CA _User Manual_


## Chapter 3: Documents...............................................................................

This chapter was added in version 2023.1
Documents are the transactions that you record in Classic Accounting.
If you were doing your bookkeeping with pen and paper a Document would be
a piece of paper with information on it. The majority of Documents would
represent a paper you get from someone else (a Bill or Check [received
payment]), or that you have as a fill-in-the-blanks form for record-keeping (Invoice
form or Checkbook).

Documents are created, edited and otherwise manipulated via forms in Classic
Accounting. See General Help on Forms (pg 29 ) for information on using the
various controls and features on document forms.

Also read and (try to, at least,) understand Transactions and their effects on
GL Accounts on page 103.

_Chapter 3: Documents_ **74** CA _User Manual_


### 3.1 Types of Documents..........................................................................................

Documents are classified into several different Groups, which largely
correspond to the different Zones in Classic Accounting. (see General Help on
Zones on pg 26 )

Within each Group are multiple documents.
Following is a breakdown of the various documents in Classic Accounting.
**NOTE:** Documents followed by a * are Non-Posting documents, see section on
Posting vs. Non-Posting

```
3.1.1Income Documents
Are used to record your Income, money coming in.
```
- Estimate (pg 274 ) *
- Sales Order (pg 275 ) *
- Invoice (pg 277 )
- Credit Memo (pg 287 )
- Receive Payment (pg 289 )
- Sales Receipt (pg 294 )

```
3.1.2Expense Documents
Are used to record your Expenses, money paid out.
```
- Quote Request (pg 238 ) *
- Purchase Order (pg 240 ) *
- Item Receipt (pg 246 ) **
- Vendor Bill (pg 250 )
- Vendor Credit (pg 255 )
- Bill Pay Check (Pay Bills, pg 256 )

** Item Receipt updates the Qty On Hand of Inventory Items, but does not post as
an Expense.

**3.1.3Banking Documents**
Represent your Checkbook. This overlaps with Expense, because a Check is
normally used to record Expenses.

- Check (see Checking, pg 321 )
- Deposit (pg 326 )
- Transfer (pg 330 )
    Both Deposit and Transfer could be classed as Internal (Company) Documents,

_Chapter 3: Documents_ **75** CA _User Manual_


as they are not linked to any Customer, Vendor or Employee.

```
3.1.4Payroll Documents
Payroll feature is not implemented, only available documents are listed.
```
- Timecards (pg 312 ) *

**3.1.5Internal (Company) Documents**
These documents can affect either Expense or Income, they do not affect
either Customers (Sales) or Vendors (Purchases), but represent financial
transactions within the company.

- Journal Entries (pg 128 )
- Manufacture (see Manufacturing, pg 130 )
- Inventory Adjustments (pg 131 )

### 3.2 Posting vs. Non-Posting....................................................................................

Each individual Document is either a **Posting** or a **Non-Posting** transaction.
**Posting** documents will affect your finances. These transactions will affect
the balance of GL Accounts (pg 86 ). A Check, an Invoice and a Journal Entry are
Posting documents.

**Non-Posting** documents do not affect your finances (at least not at time of
creation), they are for internal reference, to help you manage your business and
workflow. An Estimate and a Purchase Order are Non-Posting documents.

_Chapter 3: Documents_ **76** CA _User Manual_


### 3.3 Creating Documents.........................................................................................

To create a new document you typically open a document form with a new
(blank) document loaded, fill in the blanks, then Save the document (see Saving
Documents, pg 45 ).

Here are several ways which a new (blank / empty) document can be opened
up, though not all methods apply to all document types.

- By clicking the New button (pg 26 ) on the appropriate zone screen. See
    General Help on Zones on pg 26.
- By using The Menu Bar (pg 106 ) and selecting the "New _xxx_ " option from
    the appropriate Menu.
- By using Keyboard Shortcuts (pg 397 ).
- By clicking the Save Button (pg 41 - Save & New option) or using **Ctrl+n**
    keyboard shortcut when the correct document form is open, with an
    existing document loaded.

### 3.4 Saving Documents.............................................................................................

```
See Saving Documents, pg 45.
```
### 3.5 Recalling Documents........................................................................................

Each document type can be recalled via the appropriate Document Search
Dialog (pg 54 ). This dialog is opened in one of the following manners.

- By clicking the View/Edit button in the appropriate button group of a zone
    screen. See General Help on Zones on pg 26.
- By using The Menu Bar (pg 106 ) and selecting the " _xxxs_ ..." option from the
    appropriate Menu.
- By using Keyboard Shortcuts (pg 397 ).
- By clicking the Open Button (pg 41 )

### 3.6 Printing Documents..........................................................................................

Most documents can be printed by opening the desired document and using
the Print Button (pg 40 ) along the bottom of the form.

Many of the common documents can also be printed via the Print (batch)
button (pg 27 ) found on the Zone screens (see Batch Printing form on pg 48 ).

```
See also Printing Documents on pg 46.
```
_Chapter 3: Documents_ **77** CA _User Manual_


### 3.7 Converting (Linking) Documents.....................................................................

Both Income Zone (pg 261 ) and Expense Zone (pg 231 ) have a "Document
Chain" where a document of one type is transformed to another document type.

This chain represents the typical flow of documents, from estimating a job to
invoicing it.

Once all the line items of a document like Estimate or Sales Order have
been exported into other document(s) down the line, then the original document's
status will become _FULFILLED_.

Sometimes an order is canceled, or it is otherwise desirable to remove a
document from the OPEN documents list without deleting it. For this purpose
some document forms
have a combo-box with
**OPEN / CLOSED** status
selector somewhere in
the top right corner.
Toggling this option to
CLOSED and saving the
document will remove it
from the OPEN document
list.

**3.7.1Income side document chain:**

1. Estimate
2. Sales Order
3. Invoice

**3.7.2Expense side document chain:**

1. Quote Request
2. Purchase Order
3. Item Receipt
4. Vendor Bill

In either case you can start we any document in the chain and convert it to
any document that is further ahead in the sequence (higher number).

An Estimate can be converted directly to an Invoice (skipping the Sales Order
step), but a Sales Order cannot be converted to an Estimate (moving backward).

In the Expense side chain the Item Receipt document (pg 246 ) is used only
when dealing with Inventory Item s (pg 191 ).

_Chapter 3: Documents_ **78** CA _User Manual_


**3.7.3Cross-linking Income to Expense:**
You can also link items from a Sales Order or Estimate on the Income side to a
Purchase Order on the Expense side.

Internally in CA a cross-link is not represented in the same manner as a
regular line item link.

**A document conversion (link) is accomplished in one of the following 3 methods:**

**3.7.4Exporting to new document type**
On the top right corner of the document form you will find a button that is
labeled something like **Create Inv** , which will convert the current document to
the next document type in the chain.

If this document is eligible to convert to more than one type of document you
can find the option in this button's drop-down menu (see Drop-Down Buttons, pg
38 ).

```
This method allows exporting a single document to another one.
```
**3.7.5Importing available documents**
When creating a new document, when you select the Customer or Vendor the
system will check if this Customer / Vendor has any OPEN documents that are
eligible for linking. If one or more documents are available the Choose Items to
Import dialog will open.

This allows gathering multiple documents from behind this one in sequence
into one new document. For example, when creating a new Invoice you can
import items from one or more Sales Order and/or Estimate into a single Invoice.

**3.7.6Select Items To Import dialog**
A new dialog was added in version 2023.1, previously there were 2 documents,
one to choose which document(s) and another to choose which Items to import
from each document.

This dialog allows you to choose with Document(s) and which Items(s) to
import, by using the check-boxes. The qty of each item to import / export can be
customized by editing the numbers in the **Import** column.

_Chapter 3: Documents_ **79** CA _User Manual_


The following view shows the dialog with 2 different document, as it might
appear when invoked from a new document.

Here we have chosen (checked) only one of the two documents and unchecked
several lines from that document.

At the right end of each document line you will find numbers like **5 : 18** which
indicate the total # of lines that are checked (5) and the total Import qty of all the
checked lines (18).

At the bottom of the dialog you will find the same numbers, but for ALL
documents checked instead of just one, and also the total dollar value of all the
checked items.

```
The Collapse All button at bottom will hide the Items table of each document
```
_Chapter 3: Documents_ **80** CA _User Manual_


so you have a single line per document view like below. This can be useful if you
have a large number of documents to choose from.

There is one setting for this dialog, see Show Item Alert Notes when
Converting docs on page 142.

When importing multiple Income documents into one it will show a **Resolve
Conflicts** dialog and ask what to do, if the different documents have different
values for the document fields such as Ship Date, Ship To Address, Terms, etc.

**3.7.7Import Doc Items**
In addition to exporting documents via the Create _xx_ button and importing
documents by creating a new document, eligible document forms have an **Import
Doc Items** option in the Create _xx_
button's drop-down menu. (Invoice has
a separate button for this.)

Clicking this button will check for
available documents and show the Select
Items To Import dialog, showing all
OPEN documents of valid document
types.

Since the v2023.1 update this works
on new or existing documents, previously this option would only work on existing
documents.

This basically enables triggering the Importing available documents feature
(pg 79 ) on an existing document, and allows importing items from multiple
documents onto one even if not done all at once.

**Income Doc to Purchase Order filter**
One item of particular note in the **Import Doc Items** setup is that it enables
placing items from multiple Sales Orders (or Estimates, and even Invoices) onto a
single Purchase Order. For this particular purpose there are some special filters
for bulk importing.

When you click the Import Doc Items option on a Purchase Order (either new
or existing) you will get the Select Items To Import dialog with a special **Select**

_Chapter 3: Documents_ **81** CA _User Manual_


**Doc Type** filter at the top.

When you select the Document Type in the first box (Estimate, Sales Order or
Invoice) the second box will populate with a list of all the different Customers that
have documents of that type. Selecting a Customer will update the displayed
document list to show only the document(s) for that Customer. This makes it easy
find a particular document.

There is also a button at the right side of the filter box labeled **On S.O. Filter**.
Clicking this button will open a special dialog that allows you to import items
from Sales Order documents based on special filters.

1. **Vendor** allows you to import all items open Sales Orders that have the
    Preferred Vendor (pg 189 ) set to the Vendor of the current PO.
2. **Inventory Group** allows you to import all items on open Sales Orders

_Chapter 3: Documents_ **82** CA _User Manual_


```
belonging to a selected Inventory Group (pg 188 )
```
3. **Item** allows importing from open Sales Orders all instances of a selected
    item. This will add separate line items for each line imported. There is
    no way to combine all the items into a single row on the Purchase Order.
- If this special importer is used it will load the appropriate documents
    onto the dialog, but will only check-mark the available items matching
    the selected filter. Items that have already been placed on PO will not be
    checked. You can further customize by checking / un-checking items,
    and adjusting Import quantity.

_Chapter 3: Documents_ **83** CA _User Manual_


### 3.8 Copying & Pasting Documents..........................................................................

This feature added version 2023.1
For many of the document types you can Copy an existing document onto the
system Clipboard, then Paste it into another new or existing document.

This provides an easy way duplicate an older document, or copy some or all
line items from one document to another.

Doing a Copy & Paste does NOT create links between the documents.
If you Paste into a new document that does not have a Customer or Vendor set
it will dump all the line items and also transfer the prior document's header info
(Customer / Vendor, bill to, ship to, etc) if the source document was from the same
Zone (Income or Expense).

If you Paste into an existing document, or one that already has a name
selected, it will show the Select Items To Import dialog (pg 79 ) and allow you to
choose which item(s) to paste.

```
The Copy Doc action can be invoked in two distinct contexts.
```
- If you invoke Copy Doc from the Document Search Dialog (pg 54 ) or CA
    Search (pg 337 ) it will copy the document as it is stored in the database.
- If you invoke Copy Doc from a document form with the document loaded,
    then it will copy what is displayed on the form. This is important to know,
    because it means you can Copy a document that has not been saved!

Copy and Paste Doc can be
invoked in a number of ways.

- Keyboard Shortcuts: F7 =
    Copy Doc and F8 = Paste Doc
- The Copy Doc and Paste Doc
    options from the Edit Menu
    (pg 109 )
- The Copy Doc option on the New button's drop-down of the Doc Search
    dialog.
- The Copy Doc button on CA Search dialog.

_Chapter 3: Documents_ **84** CA _User Manual_


## Chapter 4: Accounting Basics...................................................................

So, why are you reading this? Most likely because you want to use CA to aid
you in your quest for record-keeping and Accounting.

The Author apologizes for this chapter, it is poorly presented. I believe I know
the basics of how an accounting system like CA works, but find it difficult to
explain. To learn more, and better, I recommend the **_Recordkeeping for
Christian Stewardship_** textbook by **Rod and Staff Publishers**. It is classified
as 9th grade math, simple enough that someone with an 8th grade education can
understand it, and comprehensive enough to be a great asset to your knowledge.
Even though the book does not profess to teach the double-entry accounting
system in as many words, it is actually based on double-entry accounting which
has been the standard record-keeping method for a very long time. If you take
the time to learn what this book teaches it will help you understand what happens
in the background of Classic Accounting. Most accounting software functions on
the basis of double-entry accounting, but eliminates the “double-entry” part for
the user by automatically creating the journal entries based on the action
performed, for a user-friendly and easy-to-use bookkeeping setup.

**Accounting** is the act of being Accountable for your Money, knowing where it
came from and where it disappeared to. More generally, it is the process of
keeping the necessary records to provide this knowledge.

The primary financial reports used in accounting are the **Profit & Loss** Report
and **Balance Sheet** , which we will attempt to explain after the GL Account
section.

_Chapter 4: Accounting Basics_ **85** CA _User Manual_


### 4.1 GL Accounts......................................................................................................

General Ledger, or GL Accounts (page 86 , also know an COA, Chart of
Accounts or Ledger Accounts) are the root of any accounting system. GL
Accounts track Money. All Your Money. Every Penny Of It. If you want accurate
reports, that is.

Each GL Account tracks a single entity (thing, or category). You create a
separate GL Account for each "Bank Account" (Checking, Cash, Credit Card,
Loan, Line-of-Credit, etc.) that you have, plus an account for each "category" of
income or expense that you want to track.

Within CA, GL Accounts are assigned an **Account Type** and a 4 digit **GL
Account Number**. Each Account Type has a certain range of numbers allotted
for it. This is standard accounting practice, and the CA account types and
number ranges are standard (some systems use 3 or 5 digit numbers).

```
The main areas you will want to track using Classic Accounting are:
```
**4.1.1Accounts Payable**
Accounts Payable is the money that you owe other people and businesses, for
the goods or services they provided to you. Accounts Payable is a **Liability** and is
automatically tracked with GL Account #2000.

**4.1.2Accounts Receivable**
Accounts Receivable is money that other people or businesses owe you, for the
goods or services that you provided to them. Accounts Receivable is an **Asset**
and is automatically tracked with GL Account #1200.

**4.1.3Assets**
Assets are the worth, or value, of the material and property that you own.
Tracking this category is quite complex and challenging. Having an Accountant
track this for you might be an option to consider, while using CA to track the first
2 categories. **CA can provide an accurate P&L Report if you don't track
Assents, but not an accurate Balance Sheet.**

**4.1.4Equity**
Equity is your Net Worth. Assets minus Liabilities equals Equity.
Huh? Many people have a difficult time grasping what “Equity” is. Your (or
your business's) Equity is the “Value” that you have, or the money that you Would
have – IF you were to collect all money due to you, pay all bills that you owe, and
sell all the Assets (Real Estate, Tools, Inventory, etc.) that you own.

In order to track this with a reasonable degree of accuracy you'll need to enter
all your Assets (Real Estate, Tools, etc) that you have in CA at a realistic price
(what you could expect to sell it for), and keep that price up-to-date with annual
(or quarterly) adjustments for depreciation. You'll probably need an Accountant

_Chapter 4: Accounting Basics_ **86** CA _User Manual_


to help you with this.

**Special Note** :

To actually understand how an accounting system such as CA works, it is
important to realize that a Transaction (any document or action that effects your
money or finances in any way) NEVER effects only one GL Account, it always
affects two or more GL Accounts. Well, OK, it would be possible to create a
transaction that affected only one GL Account (twice), but that creates a Debit
and Credit of equal amounts in the same account, which would be same as doing
nothing.

_In an accounting system money is not entered, it is transferred._ See
Transactions and their effects on GL Accounts on page 103 for further help on
this subject.

_Chapter 4: Accounting Basics_ **87** CA _User Manual_


### 4.2 Debits & Credits................................................................................................

The underlying principle behind all modern accounting software is based on
Double-Entry Accounting. This section added v2024.1

For every financial transaction made you create 2 (or more) **entries** in your
books (Classic Accounting). Each entry is to a **GL Account** and is either a Debit
or a Credit, based on whether the value is positive or a negative.

This provides a self-checking mechanism, the total sum of all Debits must
equal the total sum of all Credits at all times, or the books are considered “out of
balance”, meaning there is an error somewhere.

In Double-Entry Accounting, each Transaction creates both **Debit** and **Credit**
entry(s) of equal amounts.

A **Transaction** in CA is doing something (creating a document) that involves
money. Transactions do not **_create_** money, they **_move_** money by creating one or
more Debit **Entry** whose total is equal to one or more Credit **Entry** created at the
same time. Therefore a transaction always affects 2 or more GL Accounts.

When you make a sale, it **Credits** your Income account and **Debits** either your
Accounts Receivable (Credit Sale) or your Undeposited Funds (Cash Sale).

And if it's all Greek to you? Don't feel too bad. If you can grasp the basics of
how the money moves, as shown in the Transactions and their effects on GL
Accounts section on page **103** , you'll be alright.

The most direct way to create Debit and credit entries is to create Journal
Entries (page 128 ). This feature is mainly used by Accountants.

#### ===============================================

There is an “Accounting Equation” in Double-Entry Accounting, this formula
can be phrased in several ways:

```
➔ Assets = Equity + Liabilities
➔ Equity = Assets – Liabilities
➔ Liabilities = Assets – Equity
```
===============================================

You may want to know the definition of these words ( _italics from dictionary_ ):

**Assets** = All money and real property, including real estate, equipment, inventory,
etc., that you possess. _The entire property of all sorts, belonging to a person, a
corporation, or an estate_.

**Liability** = Any money or property that you owe to anyone else, including to
banks, etc. _That which one is under obligation to pay, or for which one is liable_.

_Chapter 4: Accounting Basics_ **88** CA _User Manual_


**Equity** = The portion of the Assets that you possess that you “own”, which is the
total of all your Assets minus the total of all your Liabilities. Your Net Worth
(financially speaking).

Assets, Liabilities and Equity are different “Types” of GL Accounts, plus there
are 2 sub-types of Equity; **Expense** and **Income**. _Every GL Account is one of
these 5 base Types_! See the next section for a detailed breakdown.

A common way to express the Debits and Credits is to use a T Chart as shown
below this text. **Assets** are on the left, **Liabilities** and **Equity** are on the right.

**Expense** and **Income** are expressed as a secondary T underneath Equity.
(COGS is part of Expense).

- For accounts on the Left side of a T (Assets, Expenses) a positive value is a
    Debit and a negative value is a Credit. We will call these positive balance
    accounts.
- For accounts on the Right side of a T (Liability, Equity, Income) a positive
    value is a Credit and a negative value is a Debit. We will call these
    **Negative Balance accounts** , These accounts are marked with a * in the
    GL Account Types section (pg 91 ).
- If you look on the GL Accounts form (pg 86 ) the value of negative accounts
    is reversed (negated) so it matches the value you see on the Balance Sheet
    report.
- On the GL Account Register (pg 318 ) the Payment / Deposit column values
    are opposite for Negative accounts vs. Positive accounts, again this is so it
    match the value you see on the Balance Sheet report. So on this form a
    Deposit is always an increase and a Payment is always a decrease.

The 2 most used Financial reports in a Business are the **Profit & Loss Report**
and the **Balance Sheet**.

_Chapter 4: Accounting Basics_ **89** CA _User Manual_

```
Assets (+)
D + | C -
```
```
Liabilities (-)
D - | C +
```
```
Income (-)
D - | C +
```
```
Expense (+)
D + | C -
```
```
Equity (-)
D - | C +
```

- A **Profit & Loss Report** is concerned only about the Income and Expense
    GL Accounts. It shows the amount of money you made or lost in a given
    period of time (Date Range).
- The **Balance Sheet** shows the total Assets, Liabilities and Equity of the
    business as of a given Date. In this report the total sum of all Income and
    Expense is expressed as two entries in Equity, Retained Earnings and Net
    Income.
    ◦ **Net Income** is the total of Profit or Loss of the current (report) year to
       date.
    ◦ **Retained Earnings** is the total sum of Profit or loss up to, but excluding,
       the current (report) year.

In a manual Double-Entry accounting system no number is ever entered as a
Negative, but is placed in either the Debit or Credit column based on whether it is
positive or negative, per the rules given by the T chart.

Accounting software generally stores positive and negative numbers based on
whether it is a Debit or Credit. For example, making a Deposit to Checking
(Assets) is a Debit and creates a positive entry, while writing a check (which takes
money out of Checking) is a Credit and creates an entry with a negative value.

_Chapter 4: Accounting Basics_ **90** CA _User Manual_


### 4.3 GL Account Types..............................................................................................

**GL Accounts** come in 4 basic Types: **Asset** , **Liability** , **Equity** and **Income**.
Income accounts are classed as a Sub-Category of Equity, and are further broken
down into **Income** , **COGS** and **Expense** accounts. Within Classic Accounting
these 4 basic Types are further broken down. Here are the 4 Types, and the
Account Types available within CA.

**4.3.1Asset accounts**
An Asset is something that is equal to Cash or has a Cash Value to your
business, something that can be converted to Cash when desired. Assets are
physical things such as real estate, buildings, machines, office equipment, tools,
etc. that you own, as well as any money you have, or that is owed to you. Oxford
American dictionary says an Asset is "property and possessions".

_GL Account Type:_ **Bank** : Cash or Cash equivalent; Checking, Savings
_GL Account Type:_ **Accounts Receivable** : Money Owed to You. The system
tracks this for you.

_GL Account Type:_ **Assets** : Inventory / Merchandise on Hand. Also Tangible
Personal (Business) Property such as Real Estate and Tools / Machinery.

Asset accounts have an additional setting available, **Is Current Asset** , which
places Current Assets in a separate group on the Balance Sheet report (others are
considered to Long-Term Assets).

**4.3.2** * **Liability Accounts**
A Liability is money that you owe someone else. Loans, unpaid bills, etc.
_GL Account Type:_ * **Accounts Payable** : Money you Owe to others. The
system tracks this for you.

_GL Account Type:_ * **Credit Card** : What else, a Credit Card (NOT Debit, a
debit card is a Bank account, and you would use your Checking account, a Debit
is just a different form of a Check.)

_GL Account Type:_ * **Current Liability** : Current Liability is money you owe
that is payable in full on a routine basis (not quite same as Accounts Payable).
Sales Tax is a Current Liability which the system tracks for you. Credit Cards are
a good example of a Current Liability, but they have their own account type.

_GL Account Type:_ * **Long Term Liability** : Long Term Liabilities are usually
Loans that you pay off over an extended period of time.

**4.3.3*Equity Accounts**
The Owner's Equity is your share of the value of a business, it is how much you
are worth.

```
The formula to calculate your Equity is: Total Assets minus Total Liability =
```
_Chapter 4: Accounting Basics_ **91** CA _User Manual_


Owner's Equity. That is, the total value of everything you possess, less the total
money that you owe everyone else is what you (or your business) is worth. Oxford
American dictionary says Equity is "net value of property after the deduction of
any debts".

Equity accounts are used to track the money or value that belongs to the
owner(s) of the business. You should set up a **Drawing Account** , each time the
owner(s) withdraws money or goods from the business, it should be taken from
the Drawing Account. _When a business owner takes money or goods from the
business, for whatever purpose, it is not an Expense or a COGS, it is a
DEDUCTION OF EQUITY._ The exception to this is if the business is an LLC or
some other corporation, and the owner is on the payroll.

The _3000 Opening Balance_ account is used to get all accounts to the correct
balance. Its usage will be further explained in appropriate sections.

```
GL Account Type : * Equity
```
**(*)Income Accounts**
Are used to determine the income (Profit or Loss) of a business (or person) for
a given period. The formula for calculating your Income is: Income minus (COGS
plus Expense) = Profit (or Loss). Within the system, the total Income is displayed
in the Equity account **Retained Earnings**.

If you intend to track different Categories of Income, then you will need a **set**
of Income accounts for each Category you want to track. You'll need a matching
set of Income and COGS accounts, plus if you're using Inventory Items you'll need
an Asset account and a Variance account (which also a COGS type).

_GL Account Type:_ * **Income** : Money received for sales of goods and / or
services rendered.

_GL Account Type:_ * **Other Income** : A special income type for tracking income
that is not directly from your business, such as interest earned.

_GL Account Type:_ **Cost Of Goods Sold (COGS)** : Money spend on materials,
labor and items that are re-sold, or are a portion of the product that you sell. Also
special Adjustment (Variance) accounts used for tracking Inventory.

_GL Account Type:_ **Expense** : Money spend on overhead expenses. See
further note on COGS vs. Expense on page 92.

**4.3.4COGS vs. Expense**
A **Cost Of Goods Sold** Account tracks materials and inventory received,
where the cost will be recovered when the item / material is sold. For a
manufacturing business, all materials that are a part of the finished product are
considered COGS, this includes lumber, screws, hardware, finish, etc. This also
includes Labor, both employee payroll and sub-contracted labor.

A default GL Account _5000 Inventory Purchases_ has been set up. This is the
general account to use, but it is often desirable to create additional accounts to

_Chapter 4: Accounting Basics_ **92** CA _User Manual_


track different purchases of different product lines or departments. Employee
payroll is always tracked in it's own COGS Account, and it is usually desirable to
have a separate COGS Account for sub-contracted labor, such as Finishing, as
well.

There is also a COGS account _5020 Inventory Variance_ that is used by the
system to make adjustments for Inventory Items tracking. If you use multiple
Inventory accounts, you can use only one Variance account, but it's good practice
to have a matching Variance Account for each Inventory Account.

An **Expense** account tracks Overhead Expenses. Overhead is the cost of doing
business, money that is not directly recovered by selling your products. Yes, you
will (hopefully) add enough to the selling price to cover expenses, but they are not
part of the product that is sold. Another way to look at it is; an expense is money
that is spend regardless of the amount of product made or sold. Utilities such as
phone, gasoline, electric, etc. are expenses because they are not part of the
product you sell (but you can't do business without them). Expendables are
usually expenses as well, such as sandpaper, drill bits, small tools, etc.

Certain items in a manufacturing industry could go to either COGS or
Expense, such as Glue and Putty. The important thing is to **Be Consistent!**
Always use the same account, don't jump back and forth. If you have questions if
a certain thing should be tracked as Expense or COGS, it is a good idea to contact
your Accountant and ask him / her how you should handle this.

_Chapter 4: Accounting Basics_ **93** CA _User Manual_


### 4.4 Usage of various Account Types........................................................................

**Special Note:** It is important to understand that the current balance of an
account is supposed to reflect the balance of its real-life counterpart. Here are
the various account types and how they are supposed to be used. The **Income**
accounts; _Income, Other Income, Expense and COGS, are different, because they
always increase (or decrease) on a continuous basis_ , all other account types
reflect some existing real-life money or value.

**4.4.1Bank Example: Checking**
This represents your real-life **Checking Account**. The current balance of this
account should be the actual amount of money you have available to spend. This
may not match the balance your bank has at any given moment, because of the
delay between the time you write a check and the time it is received and
processed by the bank. Each month when you receive your bank statement it
should be Reconciled with CA. See Reconciling your Checking Account on page
332.

**4.4.2Bank Example: Petty Cash**
Most businesses have some Cash on hand to pay miscellaneous expenses. The
balance of this account should match that actual cash on hand.

Whenever you take money from your checking account to refill the Petty Cash,
make a Transfer (or write a Check) From _Checking_ account To _Petty Cash_
account. This decreases your Checking balance and increases your Petty Cash
balance.

Whenever you take money OUT of the drawer to pay something, it needs to be
recorded in CA. To properly track this you should have "Petty Cash Voucher"
forms at the same location as the cash, then each time someone takes money from
the drawer he / she fills out a voucher stating how much money was taken out,
the date and what it was used for. At regular intervals someone needs to enter
these vouchers in CA. This is done by writing a Check, with the Payment Account
being Petty Cash. The Date and the GL Accounts (Expense) and Amounts must be
correct, so it will show as an Expense on the P&L Report in the proper period.
Saving the Check will decrease your Petty Cash balance.

**4.4.3Bank Example: Cash Register**
If you run a retail business that handles a lot of cash, set up a GL Account to
represent your _Cash Register_ , or Cash on Hand. The balance of this account
should match the amount of cash in the register (before trying to do a cash count,
be sure to Deposit all available cash payments to _Cash Register_ ).

_Chapter 4: Accounting Basics_ **94** CA _User Manual_


When your customer pays in cash, select Cash as the Payment Type when you
process the Payment. This will decrease your Accounts Payable and increase your
Undeposited Funds.

At regular intervals, deposit all of those Cash payments to the _Cash Register_
account using the Deposit form in the Banking section. This will decrease
Undeposited Funds and increase Cash Register.

When you remove cash from your Register to deposit into your checking
account, first create a Transfer From _Cash Register_ To account _1090 Undeposited
Funds_. Then that Transfer will be available to Deposit to the _Checking_ account.
You should not Deposit the Payments received directly to _Checking_ unless you are
actually depositing the exact lump sum of the Payment(s).

VPWR Note: Alternatively, using a transfer, move a predetermined amount of
cash into the Cash Register GL Account that will always be there for the use of
making change to customers. Each time the drawer is balanced the payments
received will be deposited into the bank account of your choice, leaving the
predetermined amount that should always be left in the drawer. The person
responsible for the accounting in the business must record any discrepancies in
balancing and record them. If an error occurs later often it can be matched to an
earlier discrepancy.

**4.4.4Credit Card Example**
Create one **Credit Card** account (we used _CSB Credit Card_ for this example)
_for_ each Credit Card you have (if you have multiple cards for one account, you
still create just one GL Account). The current balance of _CSB Credit Card_
account should be the amount you currently owe on the card.

```
When you make purchases with the card;
```
1. Create a Vendor Bill for each purchase. **Important:** Use either Line Items
    or Account Items, but enter them for the accounts / items that the purchase
    belongs to. _Example:_ If you purchased $150 worth of Ink Cartridges for
    your printer, make a $150 entry for the Expense Account _Office Expenses_
    (or similar).
2. Create a payment for this Vendor Bill, on the same date, using _CSB Credit_
    _Card_ to Pay the Bill. This will increase your _CSB Credit Card_ account
    balance.
    A. Alternate – it is also possible do this as a single step by using the Check
       (Banking Zone) using the _CSB Credit Card_ as the **Bank Account** and use
       the proper expense / COGS accounts in the Account Items table at
       bottom.

```
When you receive the Credit Card Statement;
```
1. Option 1: Use a Vendor Bill to enter your Credit Card Statement. This
    method is recommended if you will not immediately pay the Statement

_Chapter 4: Accounting Basics_ **95** CA _User Manual_


```
Balance in full.
A. Enter it as a new Vendor Bill.
```
1. **Important:** Enter the amount of new purchases as an **Account Item**
    line, using the _CSB Credit Card_ Account. This will decrease your
    _Credit Card_ account balance and (hopefully) reset it to $0.00.
2. If there is interest or other fees applied , enter that as a **separate**
    Account Item (or Line Item if you've created an appropriate Item) to
    an " _Interest Expense_ " account (interest paid is an Expense, not a
    COGS).
3. The TOTAL of the Vendor Bill should be the Total of all NEW
    transactions applied. If you are carrying a balance from one month to
    the next, this Vendor Bill amount is NOT the same as the Current
    Balance Due shown on your statement.
B.Pay the Vendor Bill entered with your checking account – just like you do
in real life.
2. Option 2: Use a Check to pay your Statement Balance in full. For the GL
Account use the Credit Card Account, e.i. _CSB Credit Card_. See section 1A
above for more details.
See Credit Cards on page 381 for additional details on this subject.

**4.4.5Long Term Liability Example: Loan**
A **Loan** you have with the bank. The current balance should show how much
money you currently OWE on the loan, NOT how much you've PAID on the loan.

See Opening Balance of Accounts (Initial Setup) on page 98 for instructions on
getting the loan account balance correct when you obtain the loan.

Each time you make a payment on that loan, create a Vendor Bill (or a Check)
for the bank and enter the amount you are paying on the Principal as an Account
Item to the _Loan_ account. Enter the Interest as a separate Account Item to an
_Interest Expense_ account (a GL Account of type Expense).

As you pay off the loan, the balance of this account should become less and
less. Once the loan is paid off in full the account balance should be $0.00. Now
set that account to Inactive and forget it!

**4.4.6Asset Account Example: Machinery**
An asset account is for tracking the value of your Property. For this example
we'll use **Machinery**. The balance of this account should be the current (Blue
Book?) value of your equipment.

At yearly intervals (or some other period determined by your Accountant) you
should make an Adjustment (Journal Entry) to deduct for the amount that your
equipment has depreciated (value lost due to wear and age). Your accountant can
give you the amount that your should depreciate each period. When you do a
Transfer you must have an account to transfer to. For depreciation this would

_Chapter 4: Accounting Basics_ **96** CA _User Manual_


probably be an Expense account _Depreciation Expenses_ , which shows on your
Profit & Loss report as an expense.

A similar account is used for **Real Estate** and each other type or class of real
property.

Assets are not part of the Profit & Loss report, but bf you don't enter your
Assets and keep them up-to-date, your Balance Sheet (pg 101 ) won't be accurate.

_Chapter 4: Accounting Basics_ **97** CA _User Manual_


### 4.5 Opening Balance of Accounts (Initial Setup)...................................................

When you create a new GL Account, the balance is $0.00. But what if it's not?
Say you're setting up your system, you create a Long Term Liability account _2250
Farmer's Loan_ for your Farmer's Bank loan, and you know that you owe
$145,552.50 on that loan. To get your initial balance, go to the Banking Menu
and create a New Transfer (pg 330 ) to move $145,552.50 **from** _2250 Farmer's
Loan_ **to** _3000 Opening Balance Equity_. The _3000 Opening Balance Equity_ is a
system default Equity Account that should be used to make all opening entries.
Don't worry about what this account's balance is!

Getting the balance correct on your checking account can be difficult if you
haven't kept your check register up to date. If you don't know the balance, one
way to do this is to leave the balance $0.00 and use the account in CA. The
balance will not be accurate, which you have to keep in mind. When Reconciling
your Checking Account (pg 332 ) enter the Balance shown on statement and check
all the transaction in CA that appear on the Statement, then write down the
**difference** amount. Leave the reconcile form, create a Transfer (Banking zone)
of the difference amount, using the _Checking_ Account and the _3000 Opening
Balance_ account. Go back to the reconcile form and check (select) the Transfer
entry, which should now be listed in the reconcile form. If it doubles your
difference instead of zeroing it, you need to reverse the From / To accounts on the
Transfer and try again. If you repeat this each month when you receive a
statement, your checking balance in CA should be correct after 3-4 month.

If you take out a NEW loan once your system is up and running, you do not use
the _3000 Opening Balance_ account. Instead you: 1. Receive the money by making
a Transfer **from** the newly created Loan account **to** the _1090 Undeposited Funds_
account. This transaction will appear in the Deposits form (Banking Zone) so you
can 2. Deposit it to your checking account and 3. Spend the money (via Vendor
Bills & Payment or Check). Alternatively, if you never actually handle the money,
you can make a single Transfer from the _Loan_ account to _Checking_ (or whatever
account it's supposed to go to, maybe it goes directly to an Asset account for a
_Machinery_ purchase).

_Chapter 4: Accounting Basics_ **98** CA _User Manual_


### 4.6 Default GL Accounts.........................................................................................

There are a number of **System Default GL Accounts** that are handled by CA,
you may not alter the account number / name or delete them. These accounts
are:

_1000 Undistributed_ (New account as of CA 2.3.3.1, usage unknown.)
1090 Undeposited Funds (This account you sometimes make Transfers to.)
1200 Accounts Receivable **(Don't mess with this.)**
2000 Accounts Payable **(Don't mess with this.)**
2010 Cash in Bank - Deficit (New account as of CA 2.3.3.1, usage unknown.)
2100 Federal With, Social Security, & Medicare (Part of payroll, not usually
used.)

3000 Opening Balance Equity (Use this account to create all initial entries
and corrections.)

3925 Retained Earnings **(Don't mess with this. Unless you're an
Accountant, they think they need to see certain numbers in here.)**

The default setup comes with quite a lot of different GL Accounts set up for
you. You should determine which of these you will use for your business, and
create a list of any additional accounts that you will need that are not already in.
The accounts you know you will not need should be modified to be an account you
will need (such as the 2 default checking accounts - just rename them to your
bank) or delete what you don't need.

_Chapter 4: Accounting Basics_ **99** CA _User Manual_


### 4.7 Tips..................................................................................................................

Create / Customize you GL Accounts using clear descriptive names, but don't
go overboard with way too many accounts or overly long names (difficult to find in
list).

For banking and liability accounts, create 1 account for each real-life banking
account, loan, line-of-credit, credit card, etc. If you bank at First Federal, you are
not tracking how much money you have in First Federal, you are tracking how
much money you have in each account that you have at First Federal.

Income and COGS accounts should be thought of as a set. Often (but not
necessarily) for each Income account (manufactured widgets sales) you will want
a matching COGS account (widget manufacturing materials). Some exceptions to
this are: 1. Employee Wages (only one COGS, regardless of number of income
accounts, unless you have some really good way of determining which portion of
your payroll goes to which category). 2. Manufacturing sales (may want multiple
income accounts for different divisions or product lines, with only one COGS
because it is too difficult to properly split the material purchases).

For Income, Expense and COGS accounts, you need to **categorize** your
accounts. You will want a separate set of accounts for each **category** of sales /
expense you are trying to track. Do NOT create a different account for each Item
you sell or purchase. If you manufacture and sell 'green widgets' and also import
and sell 'red widgets' on the side, you may want to create one set of Income /
COGS accounts for 'manufactured sales / materials' and one set for 'imported
sales / purchases'. On the other hand, if you manufacture both red and green
widgets, only one set of accounts is used. Items are used to track each individual
product, you can get reports on the number of Items sold / purchased.

_Chapter 4: Accounting Basics_ **100** CA _User Manual_


### 4.8 Financial Reports............................................................................................

**4.8.1Profit & Loss**
The **Profit & Loss** report (P&L) is a report of your **Income** family of accounts,
Income, Other Income, COGS and Expense.

This Report is always for a given time period, it has both a Start Date and an
End Date. Income account balances don't reset, they keep adding (or
subtracting). So a P&L reports the total sum of all the transactions that occurred
**within the given time period** for each GL Account of the Income, COGS and
Expense type accounts.

The P&L report groups the account totals by the Type of account; Income,
Other Income, COGS and Expense. It then applies the P&L formula: Income -
(COGS + Expense) = P or L. And gives you the total profit or loss at the end of
the reports.

**4.8.2Balance Sheet**
The **Balance Sheet** is a report of the **Current Value** of your business. It
reports on the Asset, Liability and Equity Account Types, and it is for a given
point in time. A Balance Sheet has only a time period, not a time range. It
reports each Account's Balance (sum of ALL transactions) up to, and including,
the given day.

The Balance Sheet (I'd use BS to save typing, but it sounds a bit tacky...) also
groups the accounts by their Account Type, and totals everything up in the Equity
formula: _Assets - Liabilities = Equity_.

The figure shown under Total Assets should be the total value of all your
business's property and cash. The figure under Total Liabilities should be the
total amount you owe other people. The Total Equity (if the other 2 figures are
correct) is the Owner's share of the value of the business. If the Equity is a
negative number, that is a bad thing, it means that if you sell (liquidate) your
business you will loose money out of your pocket by doing so.

**4.8.3Accrual vs. Cash Accounting
Important:** These reports are **Accrual Basis** , which means that a sale is
listed as Income when you Invoice the Customer, not when you receive the
Payment for it, and a purchase is listed as COGS or Expense when you receive
(enter) the Vendor Bill, not when you Pay the Bill. The numbers on the reports
may not be what you expect at first.

There is also a check-box option for **Cash Basis** when you run the report. It
does not list a sale as Income until the Payment is received, and Bills are not
listed as an Expense until you Pay them.

Huh? This is another area where non-accountants struggle. The numbers on
a Cash P&L can look radically different from an Accrual P&L of the same period.

_Chapter 4: Accounting Basics_ **101** CA _User Manual_


Accrual Accounting reports on the Sales you made and the Expenses you
invoked for a given period. This is regardless are the sales collected and the
expenses paid or not.

Cash Accounting reports on the money that was Collected and Paid for a given
period.

Say you sell $50,000 of goods in Jan but collect only $25,000 of it, then in Feb
you sell only $30,000 of goods but collect $25,000 of it as well as the remaining
$25,000 from Jan. An Accrual P&L shows $50,000 income in Jan and $30,000 in
Feb, but Cash shows $25,000 in Jan and $50,000 in Feb.

**The following text was kindly supplied by Alvin @ VPWR**

The **accrual method** records income items when they are earned and records
deductions when expenses are incurred. For a business invoicing for an item sold,
or work done, the corresponding amount will appear in the books even though no
payment has yet been received – and debts owed by the business show as they are
incurred, even though they may not be paid until much later.

The **cash method** of accounting, records revenue when cash is received, and
expenses when they are paid in cash. As a basis of accounting, this is in contrast
to the alternative accrual method which records income items when they are
earned and records deductions when expenses are incurred regardless of the flow
of cash.

These rules would apply to all income/expense reports including sales taxes,
vendor bills, P&L reports, graphs, etc.

Since the approval by Congress of the Tax Reform Act of 1986, the cash
method could no longer be used for C corporations, partnerships in which one or
more partners are C Corporations, tax shelters, and certain types of trusts.
Because of 1986 regulation, in general, construction businesses do not use the
cash method of accounting. Some construction businesses use the cash method;
and there are many other companies that use a modified form of the cash method,
which is acceptable under federal income-tax regulations. Under the modified
cash method of accounting, most income and expenses are determined under
cash receipts and disbursements, but purchase of equipment and of items whose
benefit will cover more than one year is to be capitalized, whereas such items as
depreciation and amortization are charged to cost. The cash method of
accounting is also used by other types of businesses, such as farming businesses,
qualified personal business corporations and entities with average gross receipts
of $5,000,000 or less for the last three fiscal years. Any questions in regards to
this, we highly recommend you discuss this with you CPA before using the system.

_Chapter 4: Accounting Basics_ **102** CA _User Manual_


### 4.9 Transactions and their effects on GL Accounts..............................................

A Transaction is moving money from one GL Account to another.
A transaction occurs whenever you create a document within CA that effects
your finances (Purchase Orders, Estimates and Sales Orders do not affect
finances).

Each transaction type (how to use CA to do it) will be covered in detail later.
From within CA, any Transaction will affect at least 2 accounts.
**The total dollar amount of 1 is always same as the total dollar amount
of 2.**

Creating an **Invoice** (page 277 ) will do the following:

1. Increase the system account **Accounts Receivable**.
2. *Increase one or more **Income** account(s).
X. Increase the Customer's balance (not part of the GL transaction).

Receiving a **Receive Payment** (page 289 ) will:

1. Decrease the system account **Accounts Receivable**.
2. Increase the system account **Undeposited Funds**.
X. Decrease the Customer's balance (not part of the GL transaction.)

Creating a **Sales Receipt** (page 294 ) will:

1. *Increase one or more **Income** account(s).
2. Increase the system account **Undeposited Funds**
(A Sales Receipt is a combination document of Invoice and Receive Payment, it
cannot be used to create "charge" sales.)

Making **Deposit** (page 326 ) will:

1. Decrease the system account **Undeposited Funds**.
2. Increase the **Bank** (checking) account it was deposited to.

Entering a **Vendor Bill** (page 250 ) will:

1. *Increase the system account **Accounts Payable**.
2. Increase one or more **COGS** and / or **Expense** account(s).
X. Increase the Vendor's balance (not part of the GL transaction).

_Chapter 4: Accounting Basics_ **103** CA _User Manual_


If you **Pay Bills** ( **Bill Pay Check** , page 256 ) it will:

1. Decreasing the **Bank** account used to pay (checking).
2. *Decrease the system account **Accounts Payable**
X. Decrease the Vendor's balance (not part of the GL transaction). 321

Writing (creating) a **Check** (Checking **,** page 321 ) will:

1. Decreasing the **Bank** account used to pay (checking).
2. Increase one or more **Expense** and / or **COGS** account(s).
(A Check skips the Accounts Payable step between a Vendor Bill and Payment.)

Issuing Refunds (page 292 ) will:

1. Increase the system account **Accounts Receivable**.
2. Decrease the **Bank** account used to pay (checking).
X. Increase the Customer's balance (not part of the GL transaction).

```
4.9.1Non-Posting Transactions:
See Posting vs. Non-Posting in Types of Documents section (pg 75 )
```
**4.9.2Tracking Inventory**
Whenever you **Purchase** an Inventory Item, the following **additional** entries
occur:

1. Increase the **Inventory Asset** account by the amount of the purchase.
2. Decrease COGS by amount of purchase, via the **Inventory Variance**
account.

In effect, this puts the purchase cost into Assets instead of COGS. It works by
creating a net COGS balance of $0.00 for the purchase, as the Inventory Variance
entry offsets the COGS entry created by the Vendor Bill. Buying Items / Material
for inventory does not show up in the total COGS on the P&L Report.

```
Whenever you Sell an Inventory Item, the following additional entries occur:
```
1. Decrease the **Inventory Asset** account by the amount of the Cost of the
Item.
2. Increase COGS by the Cost of the Item, via the **Inventory Variance**
account.

_Chapter 4: Accounting Basics_ **104** CA _User Manual_


In effect, this creates a COGS expense equal to the cost of the Item, as the
purchase cost of an Inventory Item is not considered part of the Cost of Goods
Sold until it is sold.

The Cost of an Inventory Item is a calculated figure, see Average Cost,
page 189.

When you buy Non-Inventory Items, you will show an immediate expense
(COGS) of the cost of the Items. When you sell Non-Inventory Items, you will
show an income (Profit) of the total selling price of the Item.

If you buy Inventory Items, you will not show any immediate expense. When
you sell Inventory Items, you will show an Income (Profit) only of the difference
between selling price and cost.

***** accounts are Negative Accounts, so if it says Increase, then the $ amount
applied internally to the GL Account is actually Negative, and vice versa. This is
part of the Double-Entry Accounting system, which says that every transaction
must have both Debit and Credit entries of equal amount.

_Chapter 4: Accounting Basics_ **105** CA _User Manual_


## Chapter 5: The Menu Bar........................................................................

In this Chapter we will be going through the Menu Bar along the top of the CA
window (outlined in yellow below). We'll try to tell what each option is for. The
options that have no other access then through this Menu will be explained here,
the options that are normally accessed through the Zone buttons will be covered
in their respective sections.

### 5.1 Menu Shortcuts...............................................................................................

A lot of the Menu Items have a **Shortcut** key combination listed besides them.
This is a combination of keys that can be pressed to trigger the action, instead of
using the mouse. In the **Income** menu, for example, the **New Invoice/Credit
Memo...** option has **Ctrl+I** listed besides it. That means if you hold down the
**Ctrl** (Control) key and then press and release the **I** key (lowercase, do not hold
down Shift), it will trigger that Menu Item and open a New Invoice form. If you
find yourself doing a certain action a lot, it may well be worth memorizing the
Shortcut keys for it.

**5.1.1Menu Accelerators**
The Accelerator is the underlined letter in all the top level menus and most of
the Menu options. Accelerators allow you to open the menus and 'click' the
options using your keyboard only (no mouse). Use as follows:

_Chapter 5: The Menu Bar_ **106** CA _User Manual_


- To open the desired Menu, hold down the **Alt** key and hit the desired key.
- Once the menu is open, you release the **Alt** key and hit the key matching
    the underlined character of the menu option you wish to activate.
- Example: To trigger the New Item option displayed above use **Alt + t** to
    open **Item** menu then **n** to activate the **New Item...** menu option.
- To close an open menu without activating anything, hit the **Esc** key (upper
    left key on keyboard).
- Once a menu is open you can also use the Arrow keys to navigate to the
    desired option, then hit the **Enter** key to activate it.

_Chapter 5: The Menu Bar_ **107** CA _User Manual_


### 5.2 File Menu........................................................................................................

**5.2.1New / Open / Save / Delete / Print**
These options are only enabled when a document form is loaded. Provides
some keyboard shortcuts for activating the normal actions, Open (Ctrl+O), Save
(Ctrl+S) and Print (Ctrl+P).

**5.2.2Apply Update**
This feature is for the purpose of creating an updated version of Classic
Accounting from an Update Patch file. This is used by a group of users who run
Test Releases of CA that contain early versions of new features and updates. This
will not be used by most users.

**5.2.3Exit**

This will close the Classic Accounting program. Clicking the **X** in the very Top
Right corner of the window will also close CA, there is no difference which one is
used. When you close CA, if it has been more then 3 days since your last Backup,
then it will ask if you want to Backup Database (page 118 ). You can also trigger
Exit with the Ctrl+Q keyboard shortcut.

_Chapter 5: The Menu Bar_ **108** CA _User Manual_


### 5.3 Edit Menu........................................................................................................

```
5.3.1Copy Doc
See Copying & Pasting Documents on page 84.
```
```
5.3.2Edit Doc
See previous.
```
```
5.3.3Insert Character
See Inserting Special Characters on page 57.
```
_Chapter 5: The Menu Bar_ **109** CA _User Manual_


### 5.4 Company Menu................................................................................................

Once we have the GL Accounts set up so they're usable for your business,
we're ready to enter some information about the company, set up various lists and
select the default settings to use for various purposes.

**5.4.1Company Info**
Under the
**Company**
menu, select
**Company Info**.
This information
is used to fill in
your document
(printout)
headers, so fill
in everything
that applies to
your business.

After adding
or changing
settings in this
dialog, be sure
to click the
**Save & Close**
button.
Clicking the
**Close** button
will discard your changes.

If your company has a Logo, you can display that logo on your documents
provided you have a copy of the logo in a _xxx.png_ file. Click on the **Browse**
button and select your logo. See Company Logo (pg 375 ) for details.

_Chapter 5: The Menu Bar_ **110** CA _User Manual_


**5.4.2Company Options**
When you select Company Options from the Company Menu a dialog appears
that that allows you to edit 4 different lists. These lists are used throughout the
system. Underneath each list are buttons to **Add** (create new), **Edit** (modify) and
**Delete** (remove) the selected item. The **Show Inactive** check-box will display list
items that are not Active. Setting a list item to not Active will keep it from
displaying in CA, so you don't accidentally use it.

**Terms**
The **Terms**
are a very
important part of
your CA setup.
The Terms
determine the
**Due Date** ,
**Prompt
Payment
Discount** and
**Discount Date**
for Vendor Bill s
(page 250 ) and
Customer
Invoice s (page
277 ).

The same list
is used for both
Income and
Expense
documents, so
you will need a Terms entry for all the different Terms that are on incoming Bills
as well as the Invoices you send out.

The **Terms Name** is what is displayed and printed. The standard practice for
naming Terms is the % discount, followed by the number of discount days,
followed by the word _Net_ then the Net Due days. A ready-made entry is _Due on
Receipt_ which has no discount and is due in 0 days. See Sales Tax on page 378
for a special Terms to collect a discount given for Ohio Sales Tax.

```
There are 3 options for Terms, Standard , Date Based and Fixed Date.
```
_Chapter 5: The Menu Bar_ **111** CA _User Manual_


**Standard Terms** are calculated as a
certain number of days after the document's
date. **Net Due in (days)** is how many days
from date of Invoice (or Bill) until it is due to
be paid in full. **Discount %** is what percent
discount is given (or taken, on bill) if it is paid
by **Discount if paid in (days)**. Enter 0 in the
last 2 fields if no discount is given for this
Term.

**Date Based** : A common practice is to have
a **Discount Day of Month** , such as the 10th
of the month, rather then a fixed number of
days after the Invoice / Bill date. Then the
Terms would be written as _2% 10th, Net 30th_
(or Net EOM as show here, which stands for
End Of Month). Date Based Terms are
generally
used by
companies
that bill their clients on a monthly basis,
usually at the start or end of a month, for all
the activities that occurred in the past month.
When these Terms are applied to any
document the **Due Day** and **Discount Day** will
always be in the month after the document's
date. If you create an Invoice on Feb. 13, 2015
with the Terms shown here, then the Discount
date is March 10, 2015 and the Due Date is
March 28, 2015. The **Due Day of Month** can
be up to 31
for a true
EOM date.

**Fixed Date** Terms allows presetting a
certain Date as the Due Date and Discount
Date (if applicable). This type of Terms is
normally used by businesses with seasonal
sales, to allow their customers a longer lead
time to pay large purchases.

A special **warning** applies to Fixed Date
Terms: If you use Fixed Dates, you will
probably have the same terms on a yearly
rotation. It is tempting to just modify the
existing Terms and reuse it each year. This
could have undesirable consequences if you
have any unpaid Invoices from the previous

_Chapter 5: The Menu Bar_ **112** CA _User Manual_


year, as it would change the Due Date to a year later on all existing open Invoices,
and possibly remove the Invoice from Overdue accounts and Statements list. A
better practice would be to rename the existing terms (e.i.: Due June 30 2017),
set it Inactive, then add a new terms (e.i.: Due June 30) for the current / next year.

**Warning** : In CA the % Discount of a Terms is always calculated on the
Document Total, including Freight, Sales Tax, etc. Some Accounting systems
handle the % Discount differently and do not apply the Discount to Freight, Sales
Tax and special charges. You should watch for this, and make appropriate
adjustments to the discount amount on a Payment, if you take a discount on a
Vendor Bill where such discount terms are in affect. (VPWR)

You should always double-check, and manually edit when required, the
Discount when you Pay Bills (page 256 ) and Receive Receive Payment s (page
289 ).

**Payment Methods**
The **Payment Methods** are also important,
you should have a Payment Method for each
different type of Payment that you accept.

My business does not accept Credit Cards for
Payments at this time, so I deleted or set inactive
all the Credit Card Methods in my database, but I
do occasionally receive a _Money Order_ , so I
created a Payment Type for it.

```
Via Methods
The Via Methods
(Ship Via) should also be set up for your business.
This list is simple and varies widely according to
what business you have and where your location is.
You can get creative: I created a Via Method called
Service Call in my system, to use for Invoicing
Customers that I made a service call for. It provides
a visible reference point telling how this service was
rendered.
```
```
Sales Reps
There are 2 possible ways to use the Reps list.
```
1. It can be used to track sales of different
    employees. For this usage create different
    Users (pg 125 ) for each of your employees and
    set a default Rep for each, then have each
    employee log in under their own User account
    when entering sales. Properly, this should be
    called a **Clerk** , not a Rep.

_Chapter 5: The Menu Bar_ **113** CA _User Manual_


2. It can be used to track sales made by outside **Sales Reps**. For this usage
    set a default Rep for each of your Customers (page 263 ) that is covered by
    one of your Reps. In the Reports zone, the **Customer History** report has a
    Rep filter option that allows you to generate a report for any rep for any
    given period, and see the sales history.

**QR Status**
The list of document status available on the Quote
Request form (pg 238 ) can be customized here. This is
in case you want to create custom "tags" for the status
of a QR doc.

Each entry also has an **Is Closed** tag to indicate
whether setting this status will mark the QR Doc as CLOSED or not.

There are Arrow buttons besides the QR Status combo box that can be used to
change the sequence of the statuses. Clicking an Arrow will move the currently
selected status up or down the list. The statuses are listed in the same sequence
on the QR form.

**Org Types**
Customers, Vendors and Employees
each have a "Type" field where you can
make a selection from a list. Here you can
edit the available options for that list.

First choose which list to edit by clicking
one of the options for Cust, Vend or Emp,
then add / edit items like the other lists.

**5.4.3Per Machine Settings**
Settings on this tab affect only the current machine (computer).
**_Default Doc Search Date_**
This allows you to select the default Date to use when you open the Document
Search Dialog (pg. 54 ). You can set the date (or set to No Date) that is used the
first time you open the dialog for a particular document type. As long as CA is
running, after you've opened the dialog once for a particular document type it will
'remember' that date, even if you change it. Once you close CA and restart, it will
reset to the default date set here.

_Chapter 5: The Menu Bar_ **114** CA _User Manual_


**_Show Dual Search
Boxes for
Documents_**
The default state is un-checked, if this is checked then the Document Search
Dialog (pg 54 ) will show 2 search text boxes, separated by AND as shown here.
This allows searching for 2 different criteria at the same time, such as **Miller**
AND **Sugarcreek** to find all the documents for any Miller with a Sugarcreek
address.

**_Save Trans Search Columns for Each Document Type_**
If this is checked then each document type, e.i.: Invoice, Sales Order, Check,
etc, will have its own Column Settings via the Column Widget (pg 36 ). If NOT
checked, then all document types will share the same column settings.

**_Remember Show All option on Trans Search_**
If this is checked then the "Show All" check-box on Document Search Dialog
(pg 54 ) will stay however you last used it. If not checked then Show All will
always be un-checked each time the dialog is opened. (text added v2024.1)

**_Show In-Table Search Dialog with Ctrl+F_**
The Ctrl+F key shortcut normally opens CA Search (pg 337 ), but if this
shortcut is invoked with the focus in a table control (like document line items)
then the system behavior is to open a search dialog to find text within the table.

In version 2024.1 many of the table controls were modified to overwrite this
table search feature and open CA Search instead.

```
Check this option if you prefer to have the table search dialog opened instead.
```
**_Font Size_**
The 2 **Font Size** Adjustment settings allow you to enlarge the font (text) size
in CA.

The Font Size is to allow enlarging the text when using a large high-definition
computer monitor.

**NOTE** : The Look & Feel setting that used to be in this dialog was moved to the
Choose Database dialog (pg 125 ).

**_Force Multi-Copy Printing_**
This is a work-around for a bug in version 5.x of Steward / Choreboy word
processors. For some reason on these machines certain printers refuse to print
more then one copy of a CA document. If you have this problem, try checking this
option, then setting the Print Button's **Print Action** (pg. 40 ) to
PRINT_NO_DIALOG and specifying the # of copies wanted.

```
Path for Attachments Folder
See Attachments on page 344 for more information.
```
_Chapter 5: The Menu Bar_ **115** CA _User Manual_


```
Path for Font Extensions Folder
See Jasper Reports Font Extensions on page 352 for more information.
```
**Global Settings**
This tab contains options that affect all machines (same as General and
Projects) instead of just the current machine.

Most of the settings here are Database Backup Options, see page 119 for
details.

**_Disable Country Fill_**
If this option is checked the system will leave the Country blank instead of
filling in when you type the Zip Code, see Address on page 233 for more details.

**_Convert (Org) City to ALL CAPS_**
When you enter the Zip Code on a Customer / Vendor / Employee it will
automatically fill in the City and State for you. There are 3 options here that
allow you to have the City name converted to all uppercase or entered in proper
case (if un-checked).

**Company Projects**
This uses the same form setup as Customer Jobs, but allows tracking Income /
Expense pertaining to a certain project, such as a shop expansion or similar.

See Job Tracking on page 339
for details.

```
5.4.4Org Groups Editor
See Org Groups, pg 342.
```
**5.4.5Transaction Years**
All transactions have to occur
within a Transaction Year. This is
a Calendar Year, such as 2015.
By default CA will create 1
Transaction Year, the Current
Year, when a new database is
created.

The purpose of using Transaction Years is that it allows a Year (or any
particular Month) to be **Closed** (locked). After all your end-of-year book-work is
done that year should be Closed, which will prevent anyone from creating or
modifying documents in that year, which could mess up report numbers that were

_Chapter 5: The Menu Bar_ **116** CA _User Manual_


supposed to be final.

It is not possible to save most documents if the document's date is in a Closed
or non-existent Transaction Year (or month). You CAN modify and save non-
posting documents in a closed Transaction Year. These documents are: Estimate,
Sales Order and Purchase Order.

Transaction Years automatically create
themselves when the system (Word Processor)
clock changes to a new year, but sometimes it is
desirable to manually create a new year to
enable pre or post dating documents into
another period. For example, if you're setting
up a new accounting database, you may wish to
date all of the opening balance transactions into
the previous year, so the numbers are correct as
of Jan 1 of the current year.

**5.4.6Clear All Preferences**
This clears user settings, and should
probably not be used except as a last resort, to
revert all user-selectable settings to default.
This will reset the customized table columns,
see Column Width / Position / Visibility on page
35.

```
5.4.7Clear Report Cache
See Clear Report Cache (pg 150 ).
```
**5.4.8Admin Tasks**
This opens another screen, or zone, that has buttons for the following actions.
All of theses functions require that the currently logged in user has Admin zone
access.

```
Users
Same as Users on page 125.
```
**Database Utilities**
Opens a dialog that has tools for creating and managing databases (see
Databases, page 14 )

_Chapter 5: The Menu Bar_ **117** CA _User Manual_


**_Backup Database_**
**Backup Database** creates
a _xxx_ .backup file that contains
a copy of all the data
(information) in your database
(CA accounting system). This
option is also accessible
directly from the Company
menu, **Backup Now**.

This opens a File Picker
dialog where you can select
the desired location to place
your backup file and type in a
name for it. It will
automatically prompt with
your database name as the file
name, see Global Settings (pg
116 ) for option to include date
and time in the file name. If
you name it same as an
existing backup file at the
same location, it will overwrite (replace) the existing file with a new one.

#### BACKUP IS

**IMPORTANT!** You
should create a backup
file every day when you
are using CA. The
purpose of a backup file
is twofold: 1. If for some
reason you really mess
up your accounting
system one day, you can
**Restore** the latest
_xxx_ .backup file (that is
not messed up) which
will reset all the data to
be like it was when you
created the backup file.
Then you can re-enter
the information required to bring it up to date, hopefully without messing up
again. 2. If your system crashes, e.i. your Word Processor burned out and nobody
can fix it again. If you have a backup file that you copied onto a flash drive before
you shut down last evening (you did remember to do this, not?) then you can
**Restore** that data (backup file) onto another (new / repaired) processor with CA
installed. And if the shop burns down? **A flash drive with a copy of the**

_Chapter 5: The Menu Bar_ **118** CA _User Manual_


**backup file should be at a separate location, or in a fire-proof safe.**
Multiple backup files and flash drives are a good idea.

**_Backup Options_**
There are some options on the Company Options dialog (pg 111 ) on Global
Settings tab. Most of these options are only applicable to Backup, not to restore
(at least not yet).

- **Use Plain Text format**. This causes the Backup to be created as a Plain
    Text data dump instead of the normal compressed file. The purpose of this
    option is to enable data to be transferred between different versions of
    PostgreSQL. **Warning:** On CTS Word Processors it is possible to create a
    Plain Text backup, but it is not possible to restore one. _You should not_
    _check this option unless you know why you are using it_.
    ◦ Technical info for system administrators: Standard Backup and Restore
       uses the **pg_dump** and **pg_restore** utilities (executable files) located at
       _<postgresql_install_path>/bin_. Restoring a Plain Text backup uses the
       **psql** utility instead of pg_restore.
- **Use Timestamp Based File Name**. When you do a backup CA will
    automatically suggest a backup file name, normally the database name. If
    this option is checked it will suggest a name that contains the date and
    time, like this: _2023-06-09_06-29-20_default_db.backup_. This feature
    added v2023.1.
- All the other options in the Database Backups section are for the purpose of
    including additional information in your backup file. If you open the backup
    file using a File Archiver (try 7-Zip if you are using Windows) you can view
    and/or extract the extra file(s) included because of these settings, but as of
    current CA version these files are not restored with a database restore.

**_Restore Data_**
Opens another File Picker that allows you to select an existing _xxx_ .backup file,
and reset all your information to be as it was at the time the backup file was
created.

**Warning** : This is not reversible! If you restore a Backup file, it will totally
delete everything currently in your database before loading the previously saved
data.

**_Reset Transactions and Reset All_**
These options are used to clear data from a database. Really, **you should
NOT need to be doing this**. You should not WANT to do this. One possible use
would be using the Reset Transactions to delete all the Transactions (documents)
but still retain the lists, such as Customers, Vendors, Items, GL Accounts. All the
GL Accounts would have a $0.00 balance!

**Warning** : This is not reversible, and can be fatal to your database. If you
accidentally run one of these options you will lose all information in CA. Unless
you have a backup file to Restore, you are really up a creek with no paddle in

_Chapter 5: The Menu Bar_ **119** CA _User Manual_


sight.

**_Databases Add and Remove_**
Used to create new databases and delete old ones.
The Remove will delete the currently active
(connected) database. Make sure you know what
you're doing and Why you're doing it before you use
this!

```
Warning : Deleting a database is like Reset All , see red text above.
```
**_Database Bin Path_**
Opens a small dialog
with a Browse button for
telling CA where
PostgreSQL's bin folder
is located. If this setting
is not correct the Backup
and Restore functions
will not work.

If you are using CA on a Windows based Word Processor or Computer then
this is quite different, usually "C:\Program Files (x86)\PostgreSQL\9.3\bin".

Depending on your machine and PostgreSLQ installation it may be in
"Program Files" folder instead of "Program Files (x86)". Note that the Slash (path
separator) is different in Windows (\) and Linux (/).

Your PostgreSQL version may vary as well, you really need to know and set the
exact path that is correct for your machine.

_Chapter 5: The Menu Bar_ **120** CA _User Manual_


**Import / Export Items**
Allows you to save (Export) your item list as an Excel ( _xxx_ .xls) spreadsheet file,
or to load (Import) an item list that has been saved in an Excel spreadsheet file.

**_Export Item List_**
Exporting your Items to an
Excel file is simple enough.

1. Specify the file to export to.
    Click on the **Browse**
    button along top.
    1. If you would like to
       replace an existing file,
       navigate to and select
       the file, then click Open
       on the file browser.
    2. To create a New file
       navigate to the location
       you want to save your
       file to, then enter the name of the file in the **File Name** field, including

_Chapter 5: The Menu Bar_ **121** CA _User Manual_


```
the .xls extension. The picture at right shows the File Name being
entered.
```
2. There are some Filters that enables doing an export of only some items
    1. **Active** check-box. When checked only Active items will be exported.
    2. **Item Type** lets you export only one type of Item, such as Non-Inventory
       or Inventory
    3. **Item Group** lets you export only Items that are set to a certain Inventory
       Group (pg 188 ).
3. Check all the columns you want on the exported file (In the **Exporting**
    group box) then click the **Export** button. This will create or replace the file
    you selected in step 1. When the Item list is exported an additional column
    titled **Item ID** will be included. This is an internal reference number used
    by CA, you don't need to do anything with it.
If for some reason you get an **Export
Unsuccessful** message like the one
shown here, then something did not
work. Possibly PostgreSQL is not
installed on the machine you're working
on, or maybe the Database Bin Path (pg
120 ) is incorrect. If unable to resolve
yourself you may need to contact your Classic Accounting dealer.

**_Import Item List_**
Note: A completely new Update Items by Import feature (pg 130 ) was added in
version 2020.1, and should probably be used instead of this one. This original
import setup will remain active until the developers are confident the new feature
is working as desired and can do everything the old one one does (plus more).

The Import process is more complex then Exporting. The existing Excel file
with your parts must have **Headers** in the first row (Row 1) that says what
information (data field) is in each column. At the bottom of the screen is a list of
all the column headers that can be imported. Only ITEM_NUMBER is Required,
the rest are Optional, but the spelling and capitalization of the headers in your file
must match this list exactly. If your file has column headers that are not in this
list, or are misspelled, they will be ignored during the Import. Before doing an
Import or Export you must enter a file name and location at the top (use the
**Browse** button).

**Warning** : Before doing an Item Import it is a good idea to create a backup of
your database using the Backup Database utility (pg 118 ), which can be accessed
through Menu > Company > Backup Now. Then if the Item List does not import
as desired you can restore you database as it was before you stated the Import
process.

For Importing, there are options as to what GL Accounts to use, the default
Markup Formula, etc. If you're importing a lot of parts from some external source
you may want to consider these settings and split your parts list into multiple

_Chapter 5: The Menu Bar_ **122** CA _User Manual_


files, then import them one at a time using different settings for each batch.

**Notice** : Be sure to check and correct each setting before doing an Import.
The default GL Account settings for Inventory Items may not be what you want
when you open up the Import / Export Items form.

**Note** : It will not
work to import an
OpenOffice.org (or
LibreOffice) Calc
spreadsheet in its
normal OpenDocument
format. You can create
the spreadsheet using
OpenOffice Calc, but
you will need to Save
As... (from the **File**
menu) the file in .xls
format, the **File Type:**
_Microsoft Excel 97/-
2003 (.xls)_ is what you
want.

When the **Import** button is clicked, a Progress
Dialog will appear to show that the system is
working.
When the Import is complete you'll get an
Import Results dialog, be sure to read it to see if
any Items were skipped or not successfully
imported. If an Item Number already exists in CA, then it will be skipped. This
dialog has a scroll bar, so be sure to scroll up / down to view the entire list. There
is a **Save to File** button at the bottom that allows you to save the text to a file in
case you need to refer to it for doing manual updates and cleanup.

Following is a view of a spreadsheet with items on it to import. A lot of the
fields (columns) aren't visible in this picture.

**Warning** : It is possible to set the Base Price (pg 178 ) of an Item when
importing, doing so can create a situation where the Base Price is not equal to the
Formula being applied to the Cost. If you edit the Item afterward and do anything
with the Cost or Formula, then the Price will recalculate.

_Chapter 5: The Menu Bar_ **123** CA _User Manual_


If you Import Inventory Item s (page 191 ) and have entries in the QOH
(Quantity On Hand) column, then it will create an Inventory Adjustments
document (page 131 ) during the import for generating the correct Inventory
Asset balance and QOH numbers. This Inventory Adjustment will use the
**Inventory Adjustment Acct** that is selected in the Import Items form. For
entering initial inventory balances in your system using Import Items, this should
be set to the _3000 Opening Balance Equity_ GL Account.

It is not possible to do an Item Import that sets up multiple Units (pg 190 ), it
always creates a Main Unit named _ea_. Special Note: For Inventory Items the _ea_
unit that is created by default should remain the Main Unit, if you set a different
unit as Main it may mess up your Inventory Asset value and/or QOH. You may
rename the Unit if desired, but if you intent the Main Unit to be a skid of 20
pieces and you import with 5 pieces on hand, then the QOH should be .25 (1/4
skid) when Importing (you need to create any additional Units in CA).

You should not set the Main Unit to be a skid or case quantity, the Main Unit
should always be **_ea_** , or the lowest possible sellable increment. If you want a
**_Case_** unit, add it with Multiply/Divide Main Unit setting as Multiply and enter the
number of **_ea_** in a **_Case_** in Quantity.

For the entire life of this feature there was a bug that caused the Preferred
Vendor to be set to a random Vendor. This was fixed in v2020.1. Also updated in
this version was making so the Item Number does not repeat itself in the Item
Name field, if no Item Name is set. This behavior was because Item Name used
to be a required field, but that requirement was removed quite some time ago.

```
Import / Export Names
See Import / Export Addresses on page 70.
```
**Reset Tax Migration**
This utility that was added to correct old data during a certain update of CA.
You should not need to use this.

**Fix Database Constraints**
This utility will run update routines that will attempt to fix missing database
constraints and indexes.

It should not be necessary to use this, but was added because some databases
have been found that had major issues with this.

**SQL Query Tool**
This opens a window that can be used to run updates scripts or database
queries provided by your dealer or database administrator. You should not use
this unless directed to do so by a knowledgeable programmer / administrator,
running an incorrect update could destroy your data! This is a convenience

_Chapter 5: The Menu Bar_ **124** CA _User Manual_


feature – the same functionality, and more, can be be obtained through the
pgAdmin program that is installed on the same machine as the database server
(PostgreSQL), but on some Word Processors this program can be rather awkward
to access.

**5.4.9Log In As..**
When you open CA, it
automatically logs in as User
guest. To log in as any other
user, click on **Log In As..** to
open the Login dialog. Enter
the User Name and the
password, if any. This User
Name is the **User ID** field in
the Add / Edit User dialog, not
the **Name** field.

See Securing Classic
Accounting on pg 59 for more
information on Users and
Security Zones.

**5.4.10 Log Off to Guest..**
If you are logged in as any other user then the guest user, clicking this will log
off and log back in as the guest. This usage would be for security purposes, you
might log off to guest before leaving your office for break time, etc. Read the
following section on Users for more details.

**5.4.11 Users**
See Securing Classic Accounting (pg 59 ) for information on Users and Security
Zones.

**5.4.12 Choose Database**
Use this to choose which database to connect to. This dialog was completely
rebuild with some new features in version 2020.1. See Let's get connected! on
page 15 for details on how to use this dialog.

_Chapter 5: The Menu Bar_ **125** CA _User Manual_


### 5.5 General Ledger Menu......................................................................................

In the **General Ledger** Menu are options pertain to the GL Accounts, which
we attempted to explain in the Accounting Basics chapter (page 85 ).

**5.5.1GL Accounts**
Opens the GL Accounts form. The usage of GL Accounts is discussed in
Accounting Basics, the following is how to used the forms to create and edit
accounts.

Here is a view of the **Search GL Accounts** form. Different Account Types are
different colors, and permanent system accounts have a Yellow background.

When you click on any account in the list at left, it will display information
about it in the fields at right. Along the bottom are buttons that allow you to
create a **New GL Account** (see next picture) and Edit or Delete and existing GL
Account.

**Edit and Delete GL Accounts**
The **Edit GL Account** , and **Delete this Account** buttons act on the account
that is currently selected in the list at left.

_Chapter 5: The Menu Bar_ **126** CA _User Manual_


When you Add or Edit a
GL Account, the form
shown here appears. The
fields with red *'s are
required - they can't be
blank. When you select the
**Account Type** from the
list, it will set the **GL
Range** to show you what
number range is allowed
for this account. You will
need to enter the **GL
Number** yourself, and it
may not be same as an
existing number.

The **Sub Account Of** allows you to select a "Parent" account. So far the
author has found the behavior of this setting to be rather undesirable, it does
affect some of the Reports. You can experiment with it, the selection can be
cleared again if desired.

**Account No.** allows you to fill in the Account Number of the account you're
creating (the account number your bank has assigned to your checking account)
but it is not required.

**Description** is an optional field you can use to type in a note for yourself or
other Users of CA.

**Is Current Asset** is only active if the Account Type is set to Asset. The
Balance Sheet reports will group all accounts marked as Is Current Asset into
their own sub-group.

If the **Account is Active** is un-checked, then it will no longer be available for
use. Any accounts that you don't plan to use should be either deleted or set to
Not Active, except the Default GL Accounts (page 99 ).

**Recalculate All**
The **Recalculate All** button recalculates the account balance of all accounts,
using the transactions (documents) that exist. The system should keep all
account balances correct, but if you're in doubt there's no harm in running this.

**Account Register**
Opens a dialog showing the activity of any selected GL Account. This form as
also accessible through the Register button (page 318 ) in the **Banking** zone, and
is discussed there.

_Chapter 5: The Menu Bar_ **127** CA _User Manual_


**5.5.2Journal Entries**
Opens a form that allows you to transfer funds (money) between any GL
Accounts.

To create an entry, the Debit and Credit amounts must be same. You can have
more then one Debit and/or Credit entry in the same transaction, as long as the
Total of all Debits is equal to the Total of all Credits.

Never enter a Negative number on a Journal Entry! After you make a Journal
Entry, check the Register (pg 318 ) to see if the account balances moved in the
direction they were supposed to. If not, edit the Journal Entry and reverse the
Debits / Credits. Text added v2024.1

```
For detailed information on Debits & Credits see page 88.
```
At the lower right are calculated fields showing the current total of each
column. The entry shown is creating an opening balance of $5,000.00 for the
Checking account.

The printout obtained via the Print button is just a printable document of the
Journal Entry, to be used for filing purposes. The Journal Entry's Status now
shows in top right.

```
An Attachments button (pg 344 ) was added in version 2023.1.
Since Transfer (pg. 330 ) were implemented in CA, Journal Entries are used
```
_Chapter 5: The Menu Bar_ **128** CA _User Manual_


less often, though a Transfer can't be made to any of the Income / Expense
accounts so you'll need to use a Journal Entry for that. See Standard Form
Buttons (page 38 ) for details on controls. See Opening Balance of Accounts
(Initial Setup) (pg 98 ) for additional information.

When making a **Journal Entry** you should never make a Negative entry, such
as -$50., instead you apply $50 as a (Credit / Debit) so that it will decrease the
balance.

**5.5.3Reconciliation**
Opens a form for Reconciling your checking (or any other) account. This is
described in Reconciling your Checking Account on page 332.

_Chapter 5: The Menu Bar_ **129** CA _User Manual_


### 5.6 Items Menu.....................................................................................................

The Items Menu contains options for managing your Items in CA. Items are
the things that you buy and sell.

```
5.6.1Item Manager
Opens the Item Manager, see Items, page 167.
```
**5.6.2Item Quick Edit**
Opens the Item Quick Edit
form (pg 130 ).

**5.6.3Item Bulk Edit**
Opens the Item Bulk Edit
form, see page 222.

```
5.6.4Update Items by Import
This is covered in depth in Importing / Exporting / Updating Items on pg 63.
```
**5.6.5New Item**
Opens the Items form to create a new Item. See Non-Inventory Item , page
187.

**5.6.6Inventory Groups
Inventory Groups** is a list for
the purpose of grouping your
items. Inventory Groups allow
you to filter or find Items based
on the Inventory Group they
belong to. Think of a Retail
operation where you might have
different section such as _Lawn &
Garden, Hardware, Households,_
etc.

```
See Inventory Group (pg 177 ).
```
```
5.6.7Manufacturing
See Manufacturing, page 225.
```
**5.6.8Price Levels**

See Price Levels on pg 154.

_Chapter 5: The Menu Bar_ **130** CA _User Manual_


**5.6.9Inventory Adjustments**

This form is used for adjusting current Qty On Hand of Inventory Items. You
can only add Inventory Item s to this document (see pg 191 ).

**Adjustment Account**
This will vary depending on the purpose of the adjustment.
For our initial setup, we counted and found that we have 14 Blue Widgets on
hand, so we're making an adjustment to the _3000 Opening Balance Equity_
account. We're also including other inventory we had on had at the time here,
bolts, nuts and washers.

If the boss takes a Blue Widget along home for his family to use, then it would
be adjusted using the _3500 Owner's Equity_ account.

If you need to adjust for 2 widgets that were discarded because they were
defective, you would use an Expense account of some kind, maybe create one
called _Damaged Goods_ or something like that.

**Update Item Cost**
If Checked, then it will update the Cost of the Item(s) based on the Cost
entered here. There is an **Update Item Cost** check-box on the Vendor Bill that

_Chapter 5: The Menu Bar_ **131** CA _User Manual_


will cause the Item's Cost to not update if that option is un-checked (but it cannot
force the Item to update if the Item's Update Cost From Purchases is un-checked).

**5.6.10 Memo**
This is a short description text that will display in the find Inventory
Adjustments screen, and is search-able.

**5.6.11 Notes**
This is a longer text field that can be used for a detailed explanation of how
and why you made this adjustment.

**Adjustment Line Item**
This particular adjustment is worth looking at and pointing out the way Units
work.

```
To make an Inventory Adjustment ;
```
1. Enter the Item Number.
2. Change the Item Unit, if needed.
3. Enter the quantity to adjust in the **Qty +/-** column.
4. Add additional row(s) and repeat, if needed. You can adjust as many
Items as needed on a single Inventory Adjustment.

The Blue Widgets are purchased in a Case quantity of 24 pieces. If you
examine this adjustment you will see we added 14 piece (ea) to our inventory.
The main unit is a case, which is 24 piece (ea). Our adjustment results in a Qty
Adjusted of 0.5838, a little over 1/2 case.

The **Qty on Hand** figure will always represent the Main Unit - for this Item a
Case of 24 Pieces.

**To remove Items from Inventory, use a negative number (-2) in the Qty
+/- column**.

There is a Barcode Scan Field (pg. 37 ) on this document.
A **Job** column was added to this form in v2020.1. This enables you to remove
items from Inventory and tag them to a specific Job, therefore showing as an
Expense for that Job.

```
5.6.12 Item Settings
Shows a dialog with various settings and options concerning Items.
```
_Chapter 5: The Menu Bar_ **132** CA _User Manual_


**New Item Defaults**
The options on this tab allows you to set the default GL Accounts, Formula,
Rounding and Update Cost From
Purchases that are used when
creating a new Item.

Note that the Asset and
Variance accounts are only used
for Inventory Items.

See the Price Levels section
(pg 154 ) for help with the
**Default Formula**. This is the
formula applied when no Price
Level is selected on a document.

Checking the **Update Cost
From Purchases** option will
cause this same option to be
checked by default when new
Items that are created.

The Default Rounding setting
controls the default value of Base
Price Rounding when creating
new Items. See Price Rounding Mode (pg 134 ) for details.

**5.6.13 Item Settings: Inventory Tab**

**Enable Inventory Items**
Must be checked in order to
add new Inventory Items to CA.
On a new database this option is
unchecked, new users that did
not want to use Inventory Items
frequently had problems when
they selected the Inventory
option instead of Non-Inventory
by accident.

**Inventory Method**
There is only one setting
available, Average Cost. Other
possible Inventory Methods that
might be available on more
comprehensive systems are FIFO
(First In, First Out) and LIFO
(Last In, First Out). This refers to
the Method used to calculate the Cost of an Inventory Item at the time it is sold,

_Chapter 5: The Menu Bar_ **133** CA _User Manual_


this Cost is used to make the Variance Adjustment.

```
See Average Cost on page 189.
```
**Auto-Load Item Manager**
If you have a very large number of items in your system (maybe 20,000+?) the
Item Manager can become slow to open, because it reloads the entire list each
time you open the form.

By setting this option to **No** the Item Manager will only load the Items list the
first time you open it, and not on any subsequent opening of the form. This will
cause the form to open very rapidly.

However, there is a trade-off of setting this to **No**. The displayed information
will become stale - it will not show changes made since the item list was loaded.
At any time you need up-to-date information you'll need to click on the Reload
button (pg 171 ) to update the list.

```
The way this setting works was changed in version 2023.1.
```
```
Price Rounding Mode
See Rounding with Round To on pg 165.
```
**Mfg Cost based on Components**
This setting affects how a Manufacturing document's cost will be calculated
(pg. 130 ). Initially CA always used the cost of all **Components** (Items) as the
Cost, but this can cause some accounting inaccuracies if your Components
contain Labor and/or Non-Inventory Items. From an Accountant's standpoint this
setting should be **Only Inventory** , but not everyone may agree. Most accounting
system will not allow using anything except **Inventory Items** as a Component.

**Default Inventory Adjustment GL**
Selecting a GL Account here will make so that account is pre-fill on the
Inventory Adjustments screen (pg 131 ) when you create a new Inventory
Adjustment.

```
5.6.14 Item Settings:
Other Tab
```
**Item Search Box**
For specifying how many
characters need to be typed into a
document screen's Item Combo Box
(pg. 34 ) before it starts loading the list
of available Items. Increasing this
number should make using the Item
Combo Box faster if you have a large

_Chapter 5: The Menu Bar_ **134** CA _User Manual_


number of Items.

```
For help with Price-In-Barcode patterns see page 298.
```
**5.6.15 Item Utilities**
Under the **Item Utilities** menu option there are additional sub-options, mostly
for bulk updating item Costs, Quantities and Pricing. Many of these routines
were re-written in version 2023.1 for substantial speed improvements. This section
updated v2024.1.

**Update Item Sales Tax**
Was added to fix problems that occurred when changes were made to the way
that Sales Tax is handled. Should not be necessary to use.

**Recalc Avg Cost & Pricing**
Utility that recalculates the average cost of all Inventory Items based on
transactions occurred. Run this utility if you think the Average Cost is not correct
on your items, or if the Calculated Inventory Value report (pg. 367 ) shows a
difference between the **CA Avg Cost** and **Calc Avg Cost** columns.

```
This will also recalculate the selling price of items based on the formulas.
```
**Recalc Qty On PO & SO**
Running this utility will recalculate the Qty On PO and Qty On SO numbers for
all Items.

**Reset Inventory Qty On Hand**
This is to allow users to reset the Qty On Hand figures for Inventory Item s
(page 191 ). The QOH figure will occasionally get off track, a number of bugs have
been found and corrected, but users are still requested to report any errors they
find in this area to their dealer or to CTS.

The **Invalid Inventory** report in Reports Zone should show accurate details
on actual transactions / usage for each Item that does not have an accurate QOH
figure. The Reset Inventory Count utility was added to reset the QOH numbers if
the user desires. **Warning** : If you choose to use this Utility, be sure to run and
print the Invalid Inventory report first. You may need to either make or delete
Inventory Adjustments (page 131 ) to make your numbers match up with the
actual Quantity On Hand after you reset the QOH numbers.

_Chapter 5: The Menu Bar_ **135** CA _User Manual_


```
Find Invalid Formulas
This utility will search your items for invalid Markup Formulas (pg 162 ).
```
**If you are setting up a new database and reading this from the
beginning, you should now skip forward to the Items (page 167 ), then
come back here once you've created your first items (Sales Tax and
Finance Charge).**

When you create a new Database the Sales Tax and Finance Charge items are
already in the system when you create the database, but you will still need to
modify them to be correct for your company.

```
Convert to Inventory Item
This feature is detailed in Converting Non-Inventory to Inventory on page 192.
```
_Chapter 5: The Menu Bar_ **136** CA _User Manual_


### 5.7 Income Menu..................................................................................................

Moving on to the **Income** menu. The only option in here that can't be
accessed from the Income Zone (page 261 ) is **Income Settings** and **Income
Utilities** , so that is all we'll cover here.

**5.7.1Income Settings**
Opens a dialog that has a lot of settings. This dialog has several settings that
are **Items** , so you may need to skip ahead to the Item Zone section to learn how
to create the required Items. It also has a good number of **tabs** , which we'll cover
one at a time.

```
Finance Charge tab
These settings are detailed in the Finance Charges section on page 301.
```
**General tab**
**_When Adding
New Customer_**
Here are some
settings for default
values to be used
when creating a new
Customer. Whatever
you fill in here is what
will be filled in when
you add new
Customers to CA (pg.
263 ). Note that for
Default Credit Limit
_0.00_ is equal to
unlimited. These are
the defaults, what is
already filled in for
you when you click
"New Customer".
They settings within
each Customer can be
changed on an as-
needed basis.

```
The Default Ship Via option was added in v2020.1.
```
**_Invoice Preferences_**
A couple options that affect creating Invoices. Pretty self-explanatory.
If a Customer has a Default Ship Via set (see the Customer's Additional Info
Tab on pg 266 ) then the Customer's setting will override this system-wide setting.

_Chapter 5: The Menu Bar_ **137** CA _User Manual_


**_Lock Printed Invoices_**
When checked, this option (added v2020.1) prevents Invoices from being
modified (lines cannot be added or removed, or prices modified) after it has been
printed.

This feature was requested by businesses who keep a running Invoice for
customers, but only print them once a month.

```
When Creating new Sales Order
This block contains settings for creating new Sales Order document.
```
**_Require Sales Rep on Estimate_**
Like the other "Require Sales Rep" settings, if checked this prevents an
Estimate from being saved unless the Rep field is filled in.

**Printing tab**
Contains settings for how many copies to print of various documents. This
setting is valid only if you print the document from within the document's form, if
you print documents from the Batch Printing form (page 48 ) the Copy Count
always defaults to 1.

There are various options of how documents print. If you are using
customized versions of these documents the settings will have no affect, unless
you customize a copy of a recent (v2019.1+) document.

**_Show Signature Line on [XX]_**
Option to turn the **Customer Signature** line on Invoice and other docs on and
off.

**_Show Qty Shipped on Packing Slip_**
If checked then the Packing Slip will show additional columns showing how
many items were shipped on previously. This is only valid when printed from the
Sales Order, and is useful only if part of the SO was Invoiced previously.

**_Show Qty Shipped on Sales Order_**
This shows the same extra columns on the SO print as shown on Packing Slip
when Show Qty Shipped on Packing Slip is checked.

**_Show $0.00 Tax lines on Invoice_**
Option that allows suppressing the printing of Tax line items, if the tax amount
is $0.00. This is an issue that arises in States that are required to track what non-
taxable category each sale belongs to, therefore generating tax lines that to not
have a cost.

**_Show Ordered / BO's on Invoice_**
This setting is only useful if you enter Sales Orders then generate Invoices
from it. If checked, then additional columns will appear on the Invoice showing

_Chapter 5: The Menu Bar_ **138** CA _User Manual_


the Qty that was originally ordered and how many are still not Invoiced. The only
way this information can be determined is if the Invoice was generated from a
Sales Order.

**_Show Account Balance on Invoice_**
If checked, and if you print an Invoice for a Customer that has additional
unpaid Invoices, a block with the customer's Current Balance will appear in the
bottom right of the Invoice.

**_Use #9 Window Envelopes_**
If Checked then the Logo and Address Blocks on the standard document
printout will shift to better fit a #9 Invoice Envelope, instead of the default #10
Envelope. The size and position of windows may possibly vary from brand to
brand, no guarantee that either option (checked or un-checked) will perfectly fit
your envelopes. (If neither print is close enough you can have them customized
by your CTS dealer.)

**_Title for Estimate Printout_**
By default the Estimate's printout says **Estimate** at the top of the document.
Some users might prefer to to have **Quote** , or something else there. You can
adjust that here. See Notes Line (pg. 283 ) for example.

```
Title for Packing List
There are 2 fields here for setting the title of the Packing List print (pg 286 ).
```
1. when it is printed from Sales Order
2. when it is printed from Invoice Settings added v2024.1

**Taxes tab**
Contains a list for setting which Sales Tax Item(s) is used when you create an
Invoice. See page 378 for help on Sales Tax.

**Warning:** After creating a new **Sales Tax Item** you will need to close and
reopen CA to have this Item available. If your State / County requires you to
charge and track more than one Tax, you can check all that apply. You MUST
create at least one **Sales Tax Item** and select it as the default Tax Region, CA will
not let you create Invoices without it.

**Sales Receipt tab**
This tab contains settings to better utilize CA as a **Point-Of-Sale** system.
These are all settings that only affect the Sales Receipt form and printout (pg.
294 ).

**_Default SR Copy #_**
The number of copies of Sales Receipt to print. This setting is largely invalid
as this can be configured (and is overwritten by) the Print Button (pg. 40 ).

_Chapter 5: The Menu Bar_ **139** CA _User Manual_


**_Default Cash Customer for new SR_**
If you select a Cash Customer (pg. 267 ) here it will automatically fill this
customer name in when a new Sales Receipt is created.

**_Require Sales Rep_**
If checked then a Sales Receipt cannot be saved if the Sales Rep field (pg. 32 )
is not filled in.

**_Auto-Focus for Bar
Code_**
If this is checked it will
place the focus into the
Barcode Scan Field (pg. 37 )
when a new Sales Receipt is
created.

1. If a **Default Cash**
    **Customer for new**
    **Sales Receipt** is filled
    in, then focus will be on
    scan field immediately on
    creating new SR.
2. Otherwise focus will
    jump to scan field when
    tabbing out of Customer
    Name Box (pg. 29 ) after
    selecting a Customer.

**_Clear Sales Receipt when Tender closed_**
This option, added v2020.1, adds the option of having the Sales Receipt form
automatically load a new document as soon as the Tender dialog is closed.

**_Convert Sales Receipt to Invoice_**
If a Sales Receipt is created for a customer and the Customer requests to
charge the sale instead of paying right away the Receipt can be moved to the
Invoice form using the To Invoice button at top right of SR form. These settings
allow restricting this to not allow the Invoice conversion if a Cash Customer is
entered, and has a default Ship Via that fills in when the conversion is done.

**_Sales Receipt Customer Message_**
The Sales Receipt has it's own message, as an Invoice message is often used to
express late payment penalties, etc, which are not applicable to a Sales Receipt.
The Roll Print of the Sales Receipt also includes this message. See Cust. Msgs
tab on page 143 for Invoice and Estimate messages.

```
Other Tab
Contains some miscellaneous settings.
```
_Chapter 5: The Menu Bar_ **140** CA _User Manual_


**_Create Drop-Ship PO?_**
When you create a Purchase Order from an Estimate or Sales Order, this
setting allows specifying whether or not do do a **Drop Ship** order. If you do a
Drop Ship PO then it will transfer the Customer's Name & Address to the Ship To
address of the PO instead of your Company name and address. The options for
this setting are Yes, No and Ask.

**_Info to use on PO's created from SO_**
Different businesses have different needs and methods for processing orders
and handling Items. Here are 3 check-boxes that control exactly what Item # (pg.
243 ) is used on a Purchase Order when you generate a PO from an Estimate or
Sales Order. Text in this section was updated, v2020.1.

**Always use Purchase Description if Exists**. If checked then it will use the
Item's Purchase Description instead of what is entered on the SO (usually the
Sales Description).

_Chapter 5: The Menu Bar_ **141** CA _User Manual_


**Always use Item's Item Number instead of Document's**. If checked then
it will use the Item's Item #, rather then what is entered on the Estimate / SO.

**Use Vendor Part Number when exists**. If checked, then if a Vendor's Part
Number (pg. 189 ) exists, then it will be used rather than any other Item #. (The
next overrides this, but this overrides the previous Option.)

**But use Doc Part # over VPN if it has been customized**. If checked then
if the Item # on the Estimate / SO is not same as the Item # in the Item (if you
replaced the automatically inserted Item # with a different one) then the Estimate
/ SO Item # will be used instead of a VPN. This option is invalid / disabled if
Option 1 is checked.

If NONE of of the options are checked, then it will always use the Item # as it
appears on the Estimate / SO.

```
Receive Payment Preferences
```
**Default Discount GL**

The GL Account that is used when you give a discount on an Invoice Payment
(usually for prompt payment). This is usually an Income account, which will
DEDUCT from your income on the P&L report, but it could be a COGS account
which will show as a Cost Of Goods Sold on the P&L. Either way can be correct,
you should contact your Accountant to find out how it has been handled up to this
point and continue doing it that way. This setting is the default Discount GL
Account that fills in when you process a Receive Payment (pg 289 ).

**Pay Method for Account Credit**

Here you can select a Payment Method to be automatically filled in when you
apply an Account Credit toward an Invoice. See Applying (using) the Account
Credit (pg 388 ) for more info.

**_Storewide Discount Item_**
If you select an item here it will automatically add this item to all new Income
Documents. This can be useful for stores having their annual Anniversary Sale or
similar. This would likely be used in conjunction with the Discount Item's Apply
To All (Stay @ Bottom) option (pg 216 ).

**_Disable Insufficient QOH Alert_**
Normally CA will show an alert when you try to save an Invoice when there
are not enough Qty On Hand of Item(s) on the Invoice. Checking this will
suppress the alerts. This setting added v2020.1.

**_Show Item Alert Notes when Converting docs_**
This controls whether or not an Item's Purchase Alert Note and Sales Alert
Note (pg 184 ) are displayed when a document is converted from one type to
another (like Sales Order to Invoice).

An exception to this setting is when creating a Purchase Order from an Income
document (Sales Order, etc), in this case it will always show the Purchase Alert

_Chapter 5: The Menu Bar_ **142** CA _User Manual_


Notes. This setting added version 2023.1.

**Cust. Msgs tab**
This text box is for entering a message that appears on Invoices when they are
printed. A typical message might be " _A monthly finance charge of 3% is charged
on all overdue invoices._ ", or " _We will be closed from Dec. 25 through Jan 1._ ". This
message can be changed whenever desired. The message is not saved with the
document, if you reprint an old Invoice the current Message will print.

The preview block should display the message similar to how it will appear on
Invoice (but smaller). This text can contain HTML tags to generate **bold** and
_italic_ text, etc. The preview is not quite an exact replica of the print, but close.

There is a separate message block was for Estimate. Note that the Estimate
has a considerably larger area for the message then Invoice. See also Sales
Receipt Customer Message on page 140.

**5.7.2Income Utilities**

**Update Customer Sales Tax**
This is an old utility that ensures that all Customers have all Sales Tax items
available. To the knowledge of the author this has not been an issue in recent

_Chapter 5: The Menu Bar_ **143** CA _User Manual_


years and you will probably never need to use this.

**Close Old Estimates**
If you create a lot of Estimates and only a portion of them are ever Fulfilled
you may eventually have a long list of OPEN Estimates that are no longer valid.
Selecting this option will allow you to choose a date and have the status of all
OPEN Estimates older then that date changed to CLOSED.

_Chapter 5: The Menu Bar_ **144** CA _User Manual_


### 5.8 Expense Menu.................................................................................................

The **Expense** menu is similar to Income, only the **Expense Settings** dialog is
covered here, the remaining options are accessible through the Expense Zone
(page 231 ).

```
5.8.1Expense Settings
Opens a dialog with settings for Expense Zone:
```
```
General tab
```
**_When Adding New Vendor section:_**

```
Default Type
The Vendor Type that is used when creating a new Vendor.
```
**_Default Terms_**
The Terms that are used when creating a new Vendor.
**_Default Ship Via Method_**
A default value for the Ship Via when entering a new Vendor. Added v2020.1 –
prior to this Vendor did not have a Default Ship Via setting.

**_Pay Bills Options section:_**

_Chapter 5: The Menu Bar_ **145** CA _User Manual_


**_Default Discount GL_**
the GL Account that is used when you take a discount on a Vendor Bill. See
Disc GL on 258.

This can be either an Income account, which would show the discount amount
as an Income on your P&L report, or it could be an Expense or COGS account
which would show as a DEDUCTION of Expenses (or COGS) on the P&L. You
should probably talk to your Accountant about this one.

**_Default Payment Account for Pay from Vendor Bill_**
This sets the default Payment Account for the pay from Vendor Bill feature
(see Payments (button), pg 253 ).

**_Assign Check Number from Pay Bills_**
Checking this option will allow assigning the Check Number and printing
checks directly from the Pay Bills screen. See Pay Bills on page 256 for more
information.

**_Bills Per Check_**
Sets a default value for option on the Pay Bills screen, see Bill Per Check, page
259.

```
Changing this setting will not update Pay Bills screen until you restart CA.
```
**_Other Settings on General tab:_**

**_Show Items On Order alert on Purchase Order_**
If this is checked, then when you add an Item to a PO (Purchase Order) that is
already on an existing _OPEN_ Purchase Order (not received yet) it will display a
pop-up dialog alerting you of this fact. Depending on your usage of Items and CA
as a whole, this feature could be either very nice or an extreme annoyance, which
is why there's a setting to disable it.

```
Printing tab
Contains settings;
```
**Default PO Copy Number** how many copies of a Purchase Order to print when
you click the Print button on the PO form. This should really not be used, instead
use the print settings on the Print button itself.

**Require Sales Rep** (3 check-boxes) If checked this will not allow the document
specified to be saved w/o a Sales Rep selected.

**Title for Quote Request printout** Enter the text you want to see as the title for
the Quote Request document.

**Restock List (Vendor Bill print)** A few options to customize how the Restock
List prints.

_Chapter 5: The Menu Bar_ **146** CA _User Manual_


```
Cust Msgs tab
```
Contains a place to enter text that appears on the Quote Request document.

**5.8.2Expense Utilities**

**Close Old Purchase Orders**
When not all of a Purchase Order's items are received (maybe they are Back-
Ordered or Not Available) the PO's status does not change to FULFILLED. After
awhile this can lead to an extensive list of unwanted OPEN Purchase Orders in
your list. This utility allows you to choose a date and have all OPEN Purchase
Orders older then the selected date marked CLOSED.

_Chapter 5: The Menu Bar_ **147** CA _User Manual_


### 5.9 Banking Menu.................................................................................................

The **Banking** menu is similar to Expense and Income menus, only the
**Banking Settings** can't be accessed from the Banking Zone buttons.

**5.9.1Banking Settings**

**Default Payment Account**
Sets the primary checking
account to be used throughout
the system. Whenever you create
a New Check, Pay Bill, etc., this is
the Bank account that will be
selected by default.

**Deposit Print Sort Order**
Allows adjusting the sorting of
Bank Deposit printouts by
Sequence Entered instead of by
Customer Name, if you wish.

**Reorder Check Alert**
Classic Accounting can alert
you when it is time to reorder checks.

On the Check form there is a label you can click to enter the number of checks
you currently have on hand. An alert notice will be displayed when your count of
checks on hand falls on or below the quantity enter here. This feature will track
the qty of checks on hand for each checking account.

This feature added version 2020.2, but manual not updated until v2023.1.

**Print signature on Deposits**
If you have a signature image installed for Printing Signature on Checks (pg
325 ) then you can check this option to have the same signature also print on the
Deposit Ticket print (pg 328 ).

_Chapter 5: The Menu Bar_ **148** CA _User Manual_


### 5.10 Payroll Menu.................................................................................................

Payroll is not functional, but see Payroll Zone on page 311 for details on the
features that are currently usable.

_Chapter 5: The Menu Bar_ **149** CA _User Manual_


### 5.11 Reports Menu................................................................................................

**5.11.1 Reports Menu**
This option opens the Reports Zone. See Reports Zone on page 348 for a
rundown of the available reports.

**5.11.2 Clear Report Cache**
This is mainly a convenience feature for developer purposes. The process of
creating customized reports and/or printouts involves a lot of try and try again,
and in early CA days it used to be necessary to close and restart CA for each test.
By using **Clear Report Cache** it is possible to test a printout, modify it, clear the
cache and test the new version. _You probably won't be affected by this, its
purpose is to makes Report Developing easier._

In CA, all reports and printouts (as well as most of the forms, etc) are **cached** ,
that is they are 'memorized' after they've been loaded the first time. This speeds
up the printing / loading process quite a bit. You may notice each time you open
CA and start using it, everything is slower the first time around. This is a result of
caching, it's not so much that the first time is slower than that the second time is
faster.

**5.11.3 Clear Print Button Settings**
On most document form there is a Print Button button (pg. 40 ), right-clicking
on it provides an option named **<Edit Button Settings>** , which allows setting
specific actions (copy counts, printer, etc) for this button.

Clicking on this **Clear Button Settings** menu option will clear ALL the saved
(customized) print button settings.

**5.11.4 CA Search**
This opens a dialog that allows rapid searching of transactions within CA
based on a Customer, Item Number, Description or other criterion. See CA
Search on page 337.

**5.11.5 Report Manager**
This option opens the **CA Report Manager** dialog which is described in detail
in Reports section. See Report Manager on page 349 for details.

_Chapter 5: The Menu Bar_ **150** CA _User Manual_


### 5.12 Help Menu.....................................................................................................

```
The Help menu has several options:
```
```
5.12.1 Help
Opens this help document in a separate viewer window.
```
**5.12.2 Show Log**
Opens a window that displays the Application Log. The Application Log is a
text file named applog.log that contains information on the actions and errors that
Classic Accounting is generating. This information is used by the CA developers
to find errors and often contains information that tell what happened that
generated an error.

Due to issues when running on CTS processors the location of the applog file
was changed to be inside the **prefs/logs** folder that is in Classic Accounting's
installation folder.

When you open the Log Window it reads this text file and displays it in the text
area of the Log Window. The text in this window can be copied, selected and
edited. This window has a variety of options along the bottom:

**Log Level**
Allows you to set the amount of data that gets outputted to the log. The first
option (ALL) stores the most data, and the last option (OFF) the least.

This is normally on INFO, but if you're having issues with CA your dealer may
ask you to lower the level to DEBUG or TRACE in attempt to track down the error.
As long as CA is in development it is not advisable to turn logging off, if you don't
like the big file you're getting try setting it to WARN or ERROR.

**Warning: If the log level is set to DEBUG, TRACE or ALL it can slow down
Classic Accounting!**

**Reload**
This reloads the displayed text from the actual text file, applog.log. If you
open the log window then do additional actions in CA, you will need to reload in
order to see the events generated since you opened the Log Window.

**Copy**
Copies the selected text (or all, if none is selected) to the system clipboard, so
you can paste it elsewhere (a Writer document, for example).

**Save**
Saves the currently loaded text (with modifications) to a text file. By right-
clicking this button you can save the text back to (overwrite) the applog.log file.

_Chapter 5: The Menu Bar_ **151** CA _User Manual_


**Print**
Prints the currently selected text (or all text, if none selected) to a printer.
Right-Click the button to preview instead of printing. If your system is generating
errors your dealer may want you to print a section of the app log to send to the
CA developers for analyzing. **Warning:** Printing a large app log may take a lot of
paper, ink and time! A label at the bottom shows the Line # where you last
clicked your mouse on. Scroll to the bottom and click on the last line to get the
total line count. It will print roughly 50 lines per page, so do some calculating
before you start to print a 500 page document!

**Delete**
This totally clears both the screen and the applog.log file. When you're having
issues your dealer may have you delete the log, then do the sequence of events
that generates an error or otherwise doesn't work, and fax or mail the resulting
output to your dealer or to the CA developers.

**Wrap Lines**
Changes the text area to wrap the text to the next line instead of getting a
horizontal scroll bar.

**5.12.3 About**
Displays a dialog with some information about CA, such as the current version,
what Java and PostgreSQL versions you are using, etc.

_Chapter 5: The Menu Bar_ **152** CA _User Manual_


## Chapter 6: Item Price Calculations........................................................

There are multiple factors that affect the Selling Price of an item, this chapter
attempts to summarize the various options and explain how they are used.

### 6.1 Markup vs. Margin..........................................................................................

If you wish to have a 20% Margin rather then Markup, you would use a
formula of _Cost / .8_ instead of _Cost * 1.2_.

A 20% Markup on a $100 cost is $120. If you deduct 20% from $120 you get
$96, which is less then the Cost.

A 20% Margin on a $100 Cost is $125. If you deduct 20% from $125 you get
$100, which is the Cost.

_Chapter 6: Item Price Calculations_ **153** CA _User Manual_


### 6.2 Price Levels.....................................................................................................

Price Levels allow you to sell an Item at a different price to different
Customers. The most common example would be having 2 Price Levels, _Retails_
and _Wholesale_ , where you sell products at a lower cost to other stores or volume
buyers ( _Wholesale_ customers).

A new database has only one Price Level, _Retail_.
Price Levels are added and edited through the Price Level dialog, which is
available through the Menu command: **Items > Price Levels...**

Price Levels can be added as needed, but you should take a little time to think
this through and set up the required price levels when you do your initial system
setup, it will make life easier in the future.

- Each Customer has a Default Price Level setting (pg 267 ). This Price Level
    is automatically selected on the document when you set the Customer, but
    this can be changed on a per-document basis if desired.
- Each Item in CA will have a different Selling Price for each Price Level in
    CA. See Price Levels (pg 179 ). Note that Units can also have an impact on
    the Selling Price, see pg 156.
- Each Price Level has a **Default Formula** which allows you to set a markup
    for that price level (see Markup Formulas on pg 162 )
- Each Price Level has a **Default Rounding** which allows you to set a Cents
    figure. See Price Levels on page 179 for more help.
With the current version of CA it is still possible to create Invoices WITHOUT
a Price Level. In that case, the Base Price (pg 178 ) will be used on Invoices and
other Income documents. It is recommended to always use Price Levels, even if
you have only one.

_Chapter 6: Item Price Calculations_ **154** CA _User Manual_


The default Price Level of **_Retail_** as
shown here has a formula of _Price_ , which
means it will simply use the Base Price of the
Item.

Price Levels can be edited when desired,
or can be deleted and/or new ones added.

Note that you cannot Delete a Price Level
after it has been used on documents, or is set
as customer default. If you wish to get rid of
a Price Level like this you need to un-check
the **Price Level is Active** box.

**6.2.1Updating Price Level
Formula**
When the Default Formula of a price level
is edited, there is an optional update utility
that can updates exiting Items.
For the Retail PL shown here, if the Formula was changed to
_Cost * 1.65_
then all existing Items **that currently are set at Price** can be updated to _Cost *
1.65_ , and the Selling Price updated to reflect this change.

When you save an existing Price Level with either the Formula or the Default
Rounding modified a pop-up question box will ask if you want to update existing
Items or not.

Note that it will not update the Price Level Formula or pricing of an Item if the
formula was manually changed in that item.

**6.2.2Changing Price Level on a Document**
All Income Documents (like an Invoice) have a Price Level field.
If you change Price Levels, or change the Customer to one with a different
Price Level, on a document that already has line items then CA will ask if you
want to recalculate the prices. However, if the Item has a Price of 0.00 then it
will not change back to 0.00 if you previously set a custom price.

_Chapter 6: Item Price Calculations_ **155** CA _User Manual_


### 6.3 Units................................................................................................................

This section text revised version 2024.1

Item Units enable sub-dividing bulk products into different selling quantities.
Units are added and edited on the Units Tab of Edit Item form (pg 181 ).

Each Unit has a number of different settings, here is an explanation of each
option.

**Main Unit**
One (and only one) Unit is always set as the Main Unit, and should represent
the smallest possible quantity that can be purchased or sold. The Main Unit must
always have **Multiply / Divide** set to _Multiply_ and the **Quantity** set to _1.0000_.
CA will not let you modify the Main Unit on any existing Item, even if it is not set
to _Multiply x 1_ , as doing so can create an error in the Inventory Count / Value of
your Item. Inventory Qty On Hand is tracked in terms of the Main Unit, and all
other Units are some multiples (or divisions) of the main unit.

The **Unit Name** defaults to _ea_ , but can be made whatever you wish. The unit
name should be short and descriptive, like _box_ , _12pk_ , _case_ , etc, as it prints on the
documents.

**UPC**
If you use Barcode Scanning (pg 297 ) to add items to documents then enter
(or scan) the UPC code of the item into this field. If you do enter a code beware
that each Unit needs to have it's own unique number (or text), as this is used for
lookup when scanning. It's possible to enter your own custom text or numbers in
this field if you're printing your own barcoded labels to place on the product.

```
Unit Qty
```
- **Mult/Div Main Unit:** This combo box lets you select either **_Multiply_** or
    **_Divide_** , which is used in conjunction with Quantity to determine how many
    pieces this Unit represents. See Use Multiply when possible on page 159.
- **Quantity:** This is how many "Main Units" of this product are in the Unit.
    On the Main Unit this is always 1.0 and cannot be changed. If the Mult/Div
    option is set to Divide then it is reversed and the Qty is how many of this
    Unit is in one Main Unit.

```
Default Sell / Purchase
```
- **Sellable:** If this option is un-checked then this Unit is not available to
    choose from on Income Documents (it cannot be sold). This is used if you
    buy a product in a Unit that you don't sell directly to the customer.

_Chapter 6: Item Price Calculations_ **156** CA _User Manual_


```
◦ It is not possible to make an Item non-sellable by un-checking Sellable on
all the Units of an Item. If you do it will use the Default Selling unit
when you place the Item on an Income document. Text added v2023.1
```
- **Def Selling:** Only one Unit can be set as the Default Selling Unit. This is
    the unit that is automatically set on an Income Document when you add that
    Item to the document.
    ◦ The Default Selling Unit will always be used when an item is placed on
       an Income document, regardless is it tagged as Sellable or not.
- **Def. Purchasing:** Only one Unit can be set as the Default Purchasing Unit.
    This is the unit that is automatically set on an Expense Document when you
    add that Item to the document.

**Active**
If a Unit is no longer valid for some reason, but cannot be deleted because it
has been used on documents, then you should make it in-active by un-checking
this box. If a Unit is not Active it will not be available to select from on any
document.

**6.3.2Units as Unit Of Measure**
The primary intention of Units is to provide a way to split an Item into
different quantities.

For example, if you always purchase AA batteries in a full case of 12 packs of
12 batteries per pack, but you sell them per package of 12 and also want the
ability to sell them individually, then you would create 3 separate Units:

1. A unit named **_ea_** would be the **Main Unit** and represent a single battery.
    The Main Unit must always be set as Multiply by _1_.
2. A unit named **_12pk_** would be for one pack of 12 batteries. Here you set the
    unit to **_Multiply_** by _12_. This would likely be the **Default Selling** unit.
3. A unit named **_case_** would be an entire case as you buy them. This unit
    would be set to **_Multiply_** by _144_ as there are 12 x 12, or 144, individual
    batteries (the Main Unit) per case. This would be set as the **Default**
    **Purchasing** unit, and unless you actually sell them by the case the **Sellable**
    option would be un-checked.

Here is a screenshot of the Units tab for this setup:

_Chapter 6: Item Price Calculations_ **157** CA _User Manual_


And here is a screenshot of the Price Levels setup:

Note that in the view above we used the same formula for each Unit, so the
selling price per ea (battery) is same regardless does the customer by 1 battery or
a whole case.

In most situations a larger unit (like 12pk) is sold at a lower cost-per-ea (and /
or there is a higher price for splitting a package), which is accomplished by
setting a different formula for each Unit, like this (note Base Price is changed):

**6.3.3Units as Quantity Price Break**
Another common usage of Units is to be able to provide different selling prices
of the same Item, independent of Price Levels (pg 154 ).

Often this is something like providing a price break if a certain quantity of the
same item are purchased.

For example, say an item normally sells for $10 and you wish to provide a 10%
price break for 3 or more and a 15% price break for 12 or more.

1. The Main Unit is named **_ea_** , and it is set as Default Selling
2. A new Unit is added named **_ea (3+)_** that is set to Multiply by 1
3. A new Unit is added named **_ea (12+)_** that is set to Multiply by 1
4. The price breaks are created by setting different formulas (or prices) in the
    Price Levels section on the Item's Sales tab.
    a) The Base Price is set to $10 (or whatever your selling price may be)
    **_b)_** The formula of Unit **_ea_** is set to **_Price_**
    **_c)_** The formula of Unit **_ea (3+)_** is set to **_Price*0.9_**

_Chapter 6: Item Price Calculations_ **158** CA _User Manual_


```
d) The formula of Unit ea (12+) is set to Price*0.85
```
Note that the Quantity value of all 3 Units is identical, selling a Quantity of 1
of **_Unit (12+)_** will reduce the Qty On Hand by 1, same as selling 1 of Unit **_ea_**.

Here is a screenshot of the Units tab

And a screenshot of the Price Levels formula setup

**6.3.4Proper use of Units**

**Use Multiply when possible**
It is preferred to not use **_Divide_** on new Unit setups! The idea of Dividing is
that you can set the larger unit (case) as the Main Unit then Divide it into sub-
units. This was part of CA from the beginning, but with time it became obvious
that it is not as accurate and can (does) create rounding errors in the Qty On
Hand value of Inventory Items. The preferred setup is to set the **smallest**
possible unit (even if you don't expect to sell or purchase in that unit) as the **Main
Unit** , then have all other units be multiples of it.

Using the example below with units of 1, 12 and 144, suppose we set the case
of 144 as the Main Unit and have _12pk_ Divide by 12 and _ea_ Divide by 144. Even
the 12pk unit is problematic, because when we sell a 12pk the QOH for that Item
is adjusted by 0.083333333333... (1 / 12) units. In CA all numbers are rounded
and stored at a fixed decimal value. QOH is stored at 6 decimal places (0.083333)
so after we sell 12 packages (a full case) the value adjusted from QOH is
(0.083333 * 12), or 0.999996, rather than 1.0.

_Chapter 6: Item Price Calculations_ **159** CA _User Manual_


**NOTE 1:** Sometimes using Divide is the only way to correctly resolve a Unit
update, say you have an existing Item where the main unit represents a package
of 3 pieces, but later on you decide you will open the package and sell them
individually if a customer asks. You should Never change the value of an existing
unit, so adding a new Unit with a Divide by 3 is the best way to handle this,
despite the rounding errors that it may bring.

**NOTE 2:** You should not use a Decimal number in Unit Qty. Using the Divide
operator is preferable to using Multiply with a Decimal number like 0.3333,
because the internal rounding done by CA is more accurate then the decimal
places in the Qty field allow.

**Be consistent in unit Names**
As we have seen, Units can be used for different purposes. If you utilize Units
for both Price Breaks and Quantity Breakdowns it is especially important that you
are consistent in how you name the Units.

A good practice for Price Breaks is to use the name of the unit you're selling
(like **_ea_** ) followed by the volume break in parentheses, like this: **_ea (3+)_**.

You should not use a name like **_3 pc_** for a Quantity Price Break or it will be
easily confused with a package of 3 ea.

Inversely, if you are creating a Multiply-by-3 Unit it should be named
something like **_3 pk_** , not **_ea (3)_**.

Using a name like **_doz_** instead of **_12 pk_** is common and can work fine, but you
should have a company policy for unit names and be consistent with it.

**Beware of Modifying Units**
You should never try to change the value of existing Units! Once a Unit has
been used (is on any document) then you should never try to modify its **Main
Unit** , **Mult/Div** or **Quantity** settings. Doing so can create major errors in Qty On
Hand of Inventory Items, and makes a big mess of your Item's history overall.

_It is, however, perfectly OK to rename the unit, or change the Sellable, Default
Selling and Default Purchasing options._

Not changing units includes not changing the perceived value of the Unit. A
real-life example was a CA User that was selling a product in a 3-pack, which was
the Main (and only) Unit. He opened a package and sold 1 piece from it on
customer request. To "enable" this sale in CA they tried changing the cost and
price of the item to represent 1 piece, and added another unit for 3-pack (Multiply
by 3). This will really mess up the item history because now it appears he was
buying and selling individual pieces at a much higher price in the past. If this is
an Inventory Item then the issue is much worse, because now the Qty On Hand is
incorrect. The best solution for this scenario would be to add an Each unit as

_Chapter 6: Item Price Calculations_ **160** CA _User Manual_


Divide by 3 (rename the original unit to 3-pk if needed).

**Select the Correct Unit**
A common problem for beginning CA users is to either not select the correct
Unit or enter incorrect Quantity and Price on a document, particularly on the
Expense documents (PO / Vendor Bill).

Continuing with the AA Battery item example, let's say sales are good and you
decide to invest in an entire pallet, which contains 48 _case_. When you receive a
bill it might be itemized as: "skid of AA batteries", qty 1, price $2,500.00.

It might seem correct to enter the AA Battery item on a CA Vendor Bill with a
qty of 1 and price of $2,500.00, but since you don't have a Unit representing this
volume in CA, it is not correct. It will mess up both the Qty On Hand (if it is an
Inventory Item) and the Cost (regardless what Item Type it is).

The correct method is to select the _case_ unit and enter a Qty of 48. In the
Rate field you can enter a formula to calculate the correct value per case:
_2500/48_
This will calculate the rate to be 52.08333333 and will correctly calculate the
Line Total as $2,500.00. For more info see Calculator Cells on pg 38.

**Note:** If you do make a purchase like this, beware that it can change the
selling price of the Item. IF the Item's Update Cost from Purchases option is
checked (pg 190 ) AND the Update Item Cost option on Vendor Bill form is
checked it will update the Item's Cost to $0.36168981 per _ea_ (previously, in our
example, it was $0.40). If your selling price is calculated by a formula based on
the Cost then this will recalculate your Selling Price.

In a scenario like described it is sometimes desirable to translate the volume
purchase into a higher profit rather than a lower selling price, as there is a bigger
investment (therefore more liability) involved. The Cost / Price update can be
prevented by either un-checking the **Update Cost From Purchases** option on
the Item (before you create the Vendor Bill), or by un-checking the **Update Item
Cost** option on the Vendor Bill before saving.

_Chapter 6: Item Price Calculations_ **161** CA _User Manual_


### 6.4 Markup Formulas............................................................................................

Classic Accounting utilizes Formulas to calculate the selling price of an Item
based on calculations made from the Item's Cost and/or Base Price.

**6.4.1Formula Key Words**
Certain Key Words are used in formulas to do calculations.
The Key Words are not case sensitive, for example: **Cost** , **cost** and **COST** are
considered identical and all return same results.

- **Cost** (The Item Cost (pg 194 ))
- **Price** (The Item's Base Price (pg 178 )) (Only valid in Price Level formulas)
- **AvgCost** (The Item's Average Cost (pg 189 ) (Only valid for Inventory Items)

**6.4.2Math Operators**

Mathematical calculations are done using standard math operators (as used in
spreadsheet formulas, etc).

- **+** (Add)
- **-** (Subtract)
- ***** (Multiply)
- **/** (Divide) ( **Warning: Dividing by Zero generates an error!** )
- **%** (Modulus, or MOD)
- Braces **( )** can be used to separate and/or clarify operations. For complex
    formulas it may be required to use braces to force operations to calculate in
    desired sequence.
- Spaces are usually optional, but they
    cangreatlyincreasethereadabilityoftheformula.
    **_Simple Formula Examples:_**
- Add 25% to cost: **Cost * 1.25**
- Add 20% + $1 to Cost: **Cost * 1.2 + 1** Alternate: **(Cost*1.2)+1**
- Say an item has a Cost of $100, and the markup formula is **Cost * 1.5** This
    would calculate a **Base Price** of $150.
    ◦ If you then enter **Price * 1.25** in the Formula of a Retail Price Level of
       this item, then the Retail selling price would be $187.50. ($150 + 25%)
A typical setup as used in a Wholesale or Discount business is for the Base
Price to display the Item's MSRP, either via the Markup Formula or have the price
directly entered, then use the Price Level Formula to calculate down from the
Base Price. To sell at 20% under Base Price use: **Price * .8**

_Chapter 6: Item Price Calculations_ **162** CA _User Manual_


**Beware** : _In math, multiplication and division always get done before addition
and subtraction!_ Use braces to force calculation in desired order.

For example, the formula: **Cost + .95 * 2** will first multiply 0.95 * 2 then add
that result to Cost.
To force it to add 0.95 to Cost then multiply that by 2: **(Cost + .95) * 2**

**6.4.3IF Statement**

The ternary operator, or IF statement, can be used to provide logic:

- <condition>**?** <if_value> **:** <else_value>

The "condition" of an IF statement must be True or False, so we use comparison
operators for this:

- **>** (More than)
- **<** (Less than)
- **==** (Equal To)
- **<>** (Not Equal To) Alternate: **!=**
- **>=** (More than or Equal to)
- **<=** (Less than or Equal to)

Examples:

- If cost is under $5 add 100%, otherwise add 50%: **Cost < 5? Cost * 2 :**
    **Cost * 1.5**
- If cost is $1,000 or more than add 20%, otherwise 30%: **Cost >= 1000?**
    **Cost * 1.2 : Cost * 1.3**
    ◦ Alternate way to get the same results (fewer characters): **Cost * (Cost**
       **>= 1000? 1.2 : 1.3)**
The IF statements can be stacked within each other, like this:
**Cost <= 10? Cost <= 5? Cost * 2 : Cost * 1.8 : Cost * 1.5**
which translates to: If Cost is less then or equal to $10 then if Cost is less then or
equal to $5 then Multiply Cost by 2, else (if Cost is more then $5 but less then or
equal to $10) Multiply Cost by 1.8, else (if Cost is more then $10) Multiply Cost by
1.5.

```
This might be slightly clearer if we added braces and color coded:
Cost <= 10? (Cost <= 5? (Cost * 2 ): Cost * 1.8) : Cost * 1.5
```
**6.4.4Functions**

There are numerous functions available to help with calculations:

- **int(x)** (Convert x to Integer (whole number) – drops everything after
    the decimal point)

_Chapter 6: Item Price Calculations_ **163** CA _User Manual_


- **abs(x)** (Absolute, or positive value of x – converts negative numbers to
    positive)
- **min(x,y)** (Lesser of values x and y)
- **max(x,y)** (Greater of values x and y)
- **avg(x,6)** (Average of 2 values)
- **rnd(x,n)** (Round value x to nearest n decimal places)
- **flr(x, y)** (Floor – round value x down to previous increment of y)
- **ceil(x, y)** (Ceiling – round value x up to next increment of y)

Examples:

- Lesser of 50% on Cost or 80% of Base Price: **min(Cost*1.5, Price*.8)**
- Greater of Cost + 50¢ or Cost * 1.25: **max(Cost+.5, Cost*1.25)**
    ◦ Same, rounded nearest to 2 decimals: **rnd(max(Cost+.5, Cost*1.25),**
       **2)**
- Round value of Cost + 35% up to next 5¢ increment: **ceil(Cost * 1.35, .05)**
- Round value of Cost + 35% down to 1¢ increment: **flr(Cost * 1.35, .01)**

The maximum length of all formulas is 500 characters.
If you hit F2 or Ctrl+Enter in a Formula field it will display a larger pop-up
text editor. Note that after closing the text editor you need to Tab out of the
Formula field to trigger recalculation of prices.

_Chapter 6: Item Price Calculations_ **164** CA _User Manual_


### 6.5 Rounding Prices..............................................................................................

**6.5.1Rounding with Formulas**
It is often desirable to round the result of a formula (Selling Price of an Item)
to 2 decimal places, or to a quarter, nickel, etc. See Rounding with Round To on
how to use **Round To** for rounding the results

With the **rnd** , **ceil** and **flr** function it is easy to round to x number of decimal
places within a formula. _Read the previous section carefully, rnd does not behave
same as ceil and flr!_

Prior to Price Rounding working properly and introduction of function the
following formula work-around could be used, and can still be used if desired.

You can subtract the unwanted decimal portion of the price using a MOD,
(Modulus) operation. The MOD operator is _%,_ it's function is to get the
Remainder After Division. A simple division example: _5 / 3_ = 1.6666.... Another
way of expressing this result is: 5 / 3 = 1 R2, or “5 divided by 3 equals 1
Remainder 2”. The MOD operator returns ONLY the remainder, the formula is
written: **_5 / 3 % 1_**. This divides the result of 5/3 by 1 and returns the remainder,
0.6666... Note that _5 / 3_ can be any number or formula expression that results in
a number, such as _Cost * 1.5_.

Now we can compose a formula that subtracts the remainder from the
calculation: _(5 / 3) – (5 / 3 % 1)_ = 1 Because we used _% 1_ , it is dividing by 1 and
giving the entire decimal remainder. To get to the nearest cent instead, divide
by .01, or _% .01_. You can get to a quarter by using _% .25_ , etc. **Warning:** This
rounding method always rounds down!

A more realistic formula example then the one given above – for a Cost of 9.95
we want to multiply by 1.35 and round to a nickle: _(Cost * 1.35) – (Cost * 1.35
% .05)_ = 13.40, rather then the 13.4325 that we get from _Cost * 1.35_. Note that
spaces are optional, as the complete formula is limited to 500 characters you may
eliminate all spaces to compact it if needed.

If you insist on rounding UP instead of DOWN, the following will do the trick,
but you'll need to figure out how it works yourself (Cost = 9.95): _(Cost * 1.35) +
(.05-(Cost * 1.35 % .05))_ = 13.45

**6.5.2Rounding with Round To**
On the Sales Tab the Edit Item screen (pg 188 ) there is a **Round To** field for
the Base Price, and also a **Round To** column in the Price Levels table.

Entering a valid value in this field will cause the price for that Price Level (or
Base Price) to be rounded according to the Rounding Mode that is set.

```
Rounding Mode
When a value is entered in the Round To field, the calculation method used
```
_Chapter 6: Item Price Calculations_ **165** CA _User Manual_


depends on the option selected in the Price Rounding Mode setting (Menu >
Items > Item Settings - see pg 134 ).

Price Rounding Mode is used in Items to round the selling price to a desired
precision. There are 4 possible values:

- **_EXACT_** sets the cents of the price to the RoundTo value.
- **_NEAREST_** rounds price to the nearest increment of RoundTo.
- **_FLOOR_** rounds the price down to the last increment of RoundTo.
- **_CEILING_** rounds the price up to the next increment of RoundTo.
    NOTE: EXACT accepts any decimal value. All others are evaluated to either a
whole number (1, 2, 5, etc.) or to a fractional increment of $1.00, e.i. 0.01, 0.02,
0.05, 0.10, 0.20, 0.25 or 0.50.

WARNING: If you CHANGE the setting all existing item price entries that have
RoundTo entries will be re-evaluated and re-calculated. If you change the setting
from EXACT to something else any decimal entries that are invalid will be set to
blank.

_Chapter 6: Item Price Calculations_ **166** CA _User Manual_


## Chapter 7: Items......................................................................................

You can't do anything in CA until you have Items. In this chapter we will
create one or more Item of each Item Type

An Item is created to represent each individual 'widget' or 'service' you offer
for sale. Items can also be created to represent different Asset and Expense GL
Accounts.

Each Item is **linked** to one or more GL Account (1 Account for Sales Tax, 5 for
Inventory Item and 2 for other Item Types).

The Income account is used whenever the Item is used in the Income zone
(sold).

The COGS/Expense account is used whenever the Item is used in the Expense
zone (purchased).

Items provide detail for reporting purposes. Many different items can be
linked to the same GL Accounts, thus enabling you to easily obtain the lump sum
sales ( **P&L Report** ) but also allow a breakdown of sales totals for each individual
'widget' or 'service' that you sell ( **Sales Analysis Detail by Item** and **Customer
History** Reports).

_Chapter 7: Items_ **167** CA _User Manual_


### 7.1 Item Types.......................................................................................................

Items are classed in different Item Types. When you create a new Item the
Item Type the first thing you do is specify what Item Type it is to be.

For many businesses the most commonly used Item Type is Non-Inventory
Item, so we will cover it first and explain all the available fields and settings in
detail. {Author note: VPWR states that 92% of their Items are Inventory Items,
but I'll stick to describing Non-Inventory Items first. The author had no intention
of including anything about Inventory Items when this document was first
started!}

The remaining Item Types we will cover only the details that are different from
a Non-Inventory Item.

Along the top of the form are a few General Fields that apply to the Item.
Below the General Fields are some Tabs. Each Tab has fields / settings for a
certain action or group. For instance, the Sales Tab has settings controlling what
happens when this Item is sold.

Each Item Type has different Tabs (screens with settings) available. The
**Other** Tab is available for all Item Types, even though not all of its fields pertain
to all Item Types.

**7.1.1List of Item Types**

- **Asset** - represents a capital asset, for purpose of being able to create
    documents to transfer assets, etc. Mainly used by advanced CA users.
- **Discount** - specialized item that can calculate a percent discount on a
    document.
- **Inventory** - a normal item that tracks Qty on Hand.
    ◦ Inventory Items are optional. There is an option in Item Settings:
       Inventory Tab (pg 133 ) to enable / disable the creation and importing of
       new Inventory Items. On a new database Inventory Items are disabled
       by default, if you want to use Inventory Items you'll need to enable this
       feature.
- **Non-Inventory** - a normal item that does not track Qty on Hand.
- **Other Charge** - for miscellaneous charges that are not a physical product
    you handle, Finance Charges and Shipping / Freight charges fall in this
    category.
- **Sales Tax Item** - CA handles Sales Tax as a line item on the document. The
    Sales Tax Item is quite different from other items and is automatically
    inserted and calculated based on taxable / exempt setting for the
    document's line items.
- **Service** - an item type for Labor charges.

_Chapter 7: Items_ **168** CA _User Manual_


**7.1.2Inventory vs. Non-Inventory**
For many companies one of the important decisions to make when setting up
CA is whether to use Inventory Item s (page 191 ), Non-Inventory Item s (page 187 ),
or some combination of the two.

When you start a new database you will not be able to create Inventory Items
unless you enable the setting for doing so.

This decision will affect your Profit & Loss and Balance Sheet reports. Here
are some factors to consider:

- If you use **Non-Inventory Items** the Cost of all your Items will be listed as
    a **Cost of Goods Sold** (or Expense) when you Purchase them.
- If you use **Inventory Items** the Cost of the Items will become an **Asset**
    (increasing your net worth) when you Purchase them, then be deducted
    from the Assets and become a Cost of Goods Sold when you Sell them.
- Using Inventory Items will have much **higher maintenance** for the
    Bookkeeper. Even if your accounting software works perfectly it is very
    difficult to keep track of all the nuts and bolts in a business. This
    maintenance becomes much higher in a Manufacturing environment versus
    a Retail environment, as you are buying one product and selling another
    that is composed of multiple Items.
- Using Inventory Items allows you to get a much more accurate Balance
    Sheet. Even if the numbers are not 100% you can still get a better feel of
    where you're going with your Assets. Provided this is something you care
    about?
- Using Inventory Items generally stabilizes your Profit & Loss report as
    viewed on a monthly or weekly basis. Because Inventory Items don't
    become an expense until you Sell them, your Profit will be more tied your
    Sales then to your Purchases. This is especially true if you buy Items at
    irregular or widely spaced intervals.
Think this through before you start – it is very difficult to switch from one
method to the other in midstream!

_Chapter 7: Items_ **169** CA _User Manual_


### 7.2 Item Manager..................................................................................................

```
When you open the Item Manager it will open screen as shown here.
```
**The Item Manager was completely rewritten (the way it functions internally was
changed) in version 2023.1.**

Of course, in a new database there will be only a few starter Items in here! A
newly created database will contain default items for Sales Tax, Finance Charge,
Freight and Misc Sales.

There is a label at the bottom of this screen, to the right of the **Manuf.** Button,
that shows how many items are currently displayed.

**7.2.1Adding Items**
To create a new Item click on the **Add** button along the bottom. This will open
the Edit Item form to create a new item. See Adding and Editing Items (pg 174 ).

The very first step when the Edit Item form opens is to select the desired Item
Type to use. See Item Types, pg 168.

**7.2.2Finding Items**
Once your item list has a lot of items you need an efficient way of finding the
item(s) you want.

At the top left there is a long text field for entering search text. If you click in
here and start typing it will filter the item list as you type. When you use multiple

_Chapter 7: Items_ **170** CA _User Manual_


words (separated by a space) in your search it matches each word individually,
rather then finding only the exact sequence of words you type in.

Below the search box is an option to use either AND or OR for your search. If
AND is selected it will show only items that contain all the words you typed. If OR
is selected it will show all the items that contain any of the words you entered.

**The search will look for matching words in any of these fields:**

```
✔ Item Number
✔ Item Name
✔ Sales Description
✔ Purchase Description
✔ Vendor Part Number
✔ Notes
✔ Location
```
The **Clear** button will clear the search text and reset any of the other filters
you've set.

**Filtering by Groups and Types**
To the right of the search box there are 2 controls with check-box drop-down
lists that can be used to filter the item list to selected Inventory Groups (pg 130 )
or Item Types (pg 168 ).

**Include Inactive Items**
If you check this option then any Inactive items will be included in the list.
See Item is Active on page 177.

```
Inactive Items are shown in red rows, so you can easily find them.
```
**Scan Bar Code Field**
Below the **Clear** button and **Include Inactive Items** check-box is a field for
finding Items via Barcode Scanning. If you scan for an item it will open the item
for editing rather than filter the item list.

**Reload**
This button will completely clear and reload the Item list from the database.
This is sometimes necessary in order to refresh the list to show changes made to
items.

In Item Settings there is an option for Auto-Load Item Manager (pg 134 ), if
this setting is **Yes** (the default setting) it will not be necessary to manually Reload
the item list, as it will automatically be reloaded each time you open the Item
Manager.

_Chapter 7: Items_ **171** CA _User Manual_


**7.2.3Editing Items**
Once you find the item you want, you can either double-click on it, or click
once on it (to select it) then click on the **Edit** button along the bottom. This will
open the selected Item in the Item Edit form.

You can also hit the **Enter** key to edit an item, when the desired item is
selected (highlighted).

**7.2.4Copy Item (button)**
The **Copy** button at the bottom of the Item Manager will create a copy of the
currently selected Item. To use, simply select the Item you want to copy and click
the **Copy** button.

For example, we make a copy of the 3/8" washer. Then this new Item was
edited and changed to a 1/4" washer:

Here everything looks OK, it was only necessary to change the Item Number,
Sales Description and Item Cost to create the new Item.

```
Note that Inactivate Units will not be copied to the new Item.
```
**7.2.5Item Save As**
This is not part of the Item Manager, but it fits with the Copy Item feature. On
the Item Edit screen the **Save** button has a drop-down option for **Save As** (see
Drop-Down Buttons, pg 38 ). Selecting this option will do basically the same thing
as Copy Item except it will not save the new item, instead it will open it in the Edit
Item form.

_Chapter 7: Items_ **172** CA _User Manual_


**7.2.6Deleting Items**
If you have an item in the list that you don't want you can Delete it. If the item
has not been used, that is.

Select the desired item (click on the row) then click the **Delete** button along
the bottom of the form.

If the item has not been used on any document or setting, then you should be
able to delete it, which will completely remove it from the database and the list.

Once an item has been used it cannot be deleted. However, you can set the
item as In-Active by editing the item and un-checking the **Active** check-box.

When an Item is In-Active it cannot be added to a new document, and it will
not show in the Item Manager list unless you check the **Show Inactive Items**
check-box.

You can delete more than one item at a time by selecting multiple rows in the
Item Manager. To select more than one row hold down the **Ctrl** key when clicking
on additional row(s).

You can select a range of rows by highlighting the row at one end of the range
you want, then hold down the **Shift** key and click on the row at the other end of
the range. All rows between the initial selection and the new selection will
become highlighted.

**7.2.7Manuf. button**

See Manufacturing on page 225.

_Chapter 7: Items_ **173** CA _User Manual_


### 7.3 Adding and Editing Items...............................................................................

When you add a new Item (use the **Add** button on the Item Manager, pg 170 )
you first need to select the **Item Type** you want to create (drop-down selector in
top left corner).

The Edit Item form will then load various tabs (forms / panels) based on which
Item Type you selected. Shown below is the form for **Non-Inventory** Item.

In this section we will cover the general use of the various Tabs. Different
Item Types will have only some of these Tabs.

In the following Sections we will cover each different Item Type and their use
cases.

Some Item Types have different Tabs that are specific to only that Type, these
are covered under that Item Type's section. These are Inventory Tab (pg 195 ) of
Inventory Items, and the special Tabs for Sales Tax Item (pg 212 ), Discount Item
(pg 214 ) and Asset Item (pg 218 ).

**7.3.1Form Controls (Buttons)**
Along the bottom of the form are several Buttons. Most of them should be
self-explanatory.

_Chapter 7: Items_ **174** CA _User Manual_


**Save Button**
Saves the current Item as displayed. This button has a drop-down, see Save
Button (pg 41 ).

```
You can also Save the current form (without clearing it) using Ctrl+S.
```
**Delete Button**
Deletes the currently displayed Item from the database.
This action will be successful only if the Item has never been used. If the Item
is on any document anywhere in Classic Accounting then you will get an error
message if you attempt to delete it.

If you cannot delete an Item that you no longer have, etc, then you can set it to
In-Active instead. Un-check the **Item is Active** check-box at the bottom left
corner of the form and Save, then the Item will no longer show in your lists, etc.

**Open Button**
Most Open buttons in CA will display a pop-up to select some document to
Open, but in Edit Item this button toggles back to the Item Manager (pg 130 )
instead. From here you can choose a different Item to edit.

If the currently displayed Item has un-saved changes then you'll get a message
asking if you want to save your changes first. Sometimes you get this message
even if you didn'tf change anything, clicking into a table control will usually "flag"
the form as modified even if you did not change anything.

**Go Back Button**
This will close the Edit Item form and go back to the previously displayed
form. It will ask to save any changes, same as the Open button.

**<< Prev / Next >> Buttons**
The Previous Item / Next Item buttons at the bottom left corner will move you
through the item list, one Item at a time.

The Ordering used by this feature is the Items are sorted first by **Item Type** ,
then by **Item Number**.

So if your currently displayed item is a Discount Item, then Next / Prev will
take you through all the Discount Items. If you move before (<<) the Discount
items you'll go into the Asset Items, and if you move past (>>) the Discount items
you'll go into the Inventory items.

It also syncs with the current item's **Item is Active** setting, if your displayed
item is active then only active items will be cycled through, and vice versa.

_Chapter 7: Items_ **175** CA _User Manual_


**7.3.2General (Shared) Item Fields**
Along the top of the Edit Item form are a few fields that are common to all
Item Types.

**Item Type**
This determines what Type of Item this is, it is the first thing you must select
when creating a new item.

This selection cannot be changed! If you accidentally choose the wrong one
then just click Go Back (or Ctrl+N for "New Item") and try again.

The only option to change the type of an existing Item is to convert a Non-
Inventory Item into an Inventory Item, see Change To Inventory on page 188.

**Item Number**
Every Item must have an Item Number. This is the primary "code" for
identifying your Item.

This field name is a bit misleading, it does not need to be a Number in the
sense of being numerical, it can be any text. For a really example a 24-pack of
Energizer AA batteries might be: _ENER-AA 24_

If you create your own item numbers (codes) it is good practice to have a
consistent style / format. To follow up on the previous example, for a 12 pack of
Duracell AAA the Item # should be similar to: _DURA-AAA 12_. It should not be a
different format, like: _AAA-12, Duracell_.

**Item Name**
This field is optional, it can be left blank. This field shows throughout the
system when you enter Items on documents, etc, but it does display anywhere
that your Customer or Vendor can see it.

The most common usage of this field is to use it to indicate the Brand Name or
some other field that aids in helping you find the item. Item Name is one of the
fields that is matched when you search for an Item throughout the system, like in
the Item Combo Box (pg 34 ).

_Chapter 7: Items_ **176** CA _User Manual_


**Inventory Group**
Inventory Groups is a list that you create yourself, see Inventory Groups on
page 130.

Inventory Groups are useful for grouping items together that you want to edit
or otherwise use / view / group at one time. Some Inventory Reports (pg 366 )
have an option to group results by Inventory Group.

Inventory Groups are often either a list of different Categories of Items, like
_Filters_ , _Mufflers_ , _Spark Plugs_ , etc, or as a list of different Manufactures, like
_Honda_ , _Briggs_ , _Kawasaki_ , etc.

```
Item is Active
```
The **Item Is Active** check-box is at the bottom left of the Edit Item form.

Sometimes it is desirable to remove an Item from the item list, because it is
discontinued or otherwise not used anymore.

If the Item has been used in transactions it cannot be Deleted, but you can set
it Inactive instead by un-checking this option.

When an Item is not active it will disappear from the lists and will not be used
anymore. On the Item Manager there is an option for Include Inactive Items (pg
171 ), this allows you to find and edit items that have been set as inactive.

```
You can change an inactive item back to active again, if desired.
```
**7.3.3Sales Tab**
The **Sales** tab contains settings that apply when this Item is Sold, when it is
used on an Income document.

**Sales Description**
This is the Description text on a document, it is what the customer sees on the
Invoice or other document printout. This field accepts up to 3,000 characters.

_Chapter 7: Items_ **177** CA _User Manual_


The Description text on the document can be edited as desired, this Sales
Description is just the default that loads when you select the item. For example, if
this is a "Special Parts" item, then you may want to leave this field blank and just
custom type whatever needed on each document.

**Sales Account**
The **Sales Account** is the GL Account that is used when the Item is sold. This
is that all-important LINK between GL Accounts and Items. It is normally an
**Income** GL Account.

This auto-fills with the **Item Default Sales GL** in Item Settings, see New Item
Defaults on pg 133.

```
This is a required field, may not be blank!
```
**Item Cost**
The **Item Cost** is what you pay for the Item. If this is not something you buy
you may leave the cost at 0.00.

Cost can be used as a factor for calculating the Selling Price.
This field is the same as the Item Cost on the Purchase Tab (pg 179 ), changing
one will change the other.

**Markup Formula**
The **Markup Formula** is a calculation applied to the Cost to get the **Selling
Price**. For help with Markup Formulas see page 162. This particular field auto-
fills with the **Default Markup Formula** that is in the Item Settings dialog (pg
132 ).

If you don't want to use a Formula, you can leave this field blank then
manually enter a Base Price. The drawback (or advantage) of doing so is that
when the Cost of the item changes it will not affect the Selling Price.

A Base Price column in Vendor Bill Line Items (pg. 252 ) allows modifying the
Base Price directly from the Vendor Bill **if** there's a price entered instead of a
formula. See the following Base Price for more information.

**Base Price**
The **Base Price** is the calculated **Selling Price** of the item. This field displays
the price that the Customer is charged when No Price Level is selected on an
Invoice.

This field is more typically used for the MSRP (Manufacturer's Suggested
Retail Price) of the Item, either calculated from the Item Cost via a Markup

_Chapter 7: Items_ **178** CA _User Manual_


Formula or manually entered (with the Markup Formula being blank).

If you choose to leave have a manually entered Base Price, then you can
change the Base Price from the Vendor Bill's Markup % and Base Price columns
when you process Item purchases.

The Base Price will display up to 8 decimal places, but you can use Round To
to round the value if desired.

Customized Sales Order / Invoice printouts are available to display the Base
Price of the Item, if so desired. This is often desirable for Wholesale businesses
who want to display the Base Price so the buyer (typically a Retail business) can
see the Item's current MSRP.

**Round To**
This setting controls the Price Rounding of the Base Price. See Price
Rounding Mode on page 134 for details.

If this is blank, then no rounding is done on the Base Price except to limit it to
8 decimal places.

**Price Levels**
The **Price Levels** table beneath the General Fields controls the Selling Price
that the Customer is charged when that particular Price Level is selected in an
Invoice or other Income document.

There is an entry in this list for each Price Level multiplied by each Unit of this
Item. See Units Tab on page 181 for and Price Levels on page 154 for setup
details.

**7.3.4Purchase Tab**
The **Purchases** tab contains settings that apply when this Item is Purchased,
when it is used on an Expense document.

_Chapter 7: Items_ **179** CA _User Manual_


**Item Purchase Description**
This is the text that auto-fills as the line's Description when this Item is placed
on an Expense document (Purchase Order, Vendor Bill, etc).

This is just the "default" text, you can customize or replace it as needed each
time you use it on a document.

NOTE: This field may be blank! If you don't fill anything in here it will use the
Sales Description (pg 177 ) instead.

**Purchase/COGS Account**
The **Purchase/COGS Account** is the GL Account that is used when the Item
is purchased. This is that all-important LINK between GL Accounts and Items.
This is normally either a **COGS** or an **Expense** GL Account, see COGS vs.
Expense on page 92 for more information.

This auto-fills with the **Item Default Purchase GL** in Item Settings, see New
Item Defaults on pg 133.

```
This is a required field, may not be blank!
```
**Item Cost**
This is the Cost of the Item, expressed in the cost of the Main Unit.
This field is the same as the Item Cost field on the Sales Tab (pg 177 ),
changing one will change the other.

**Avg Cost**
This calculated field is non-editable, it shows the current **Average Cost** of the
Item (expressed in value of the Main Unit).

This field applies only to Inventory and Asset Items, all other Item Types it will
always show 0.00.

When you sell an Inventory Item, this is the amount that is used for the
**Inventory Variance** and **Asset Value** adjustment.

If you feel this number is not correct, try running the Recalc Avg Cost &
Pricing utilities (pg 135 ) that is in the Items Menu.

```
Preferred Vendor
```
_Chapter 7: Items_ **180** CA _User Manual_


**Vendor Part Number**
This field is for the part number you use to order the item from your Vendor.
Fill this in only if this is different from the Item Number.

**Update Cost From Purchases**
If this option is checked then the item's Cost will update if you place the item
on a Vendor Bill or Item Receipt with a different price.

Beware that in order for the price to update the Update Item Cost option on
the document form (pg 251 ) must be checked when you save it.

**Order Min**
The minimum Qty to order. This is the Qty that will fill in when the item is
placed on an Expense document (Purchase Order, Vendor Bill, etc.).

**Order Max**
The maximum Qty to order. This is for reference only, does not limit or control
anything.

**7.3.5Units Tab**
The **Units tab** allows you to sub-divide case (bulk) quantities into resale
packages. Units can also be utilized for other things, such as providing different
price breaks for quantity purchases.

```
Other accounting systems may call this a Unit Of Measure.
See Units on page 156 for more details on using Units.
```
**_Unit Example 1:_**
If you always purchase AA batteries in a full case of 12 packs of 12 batteries
per pack, then you would probably create 3 separate Units. The first, and **Main
Unit** , would be _ea_ , per individual battery. Another Unit of _case_ would be a full
case of 144 batteries, it would bet set to Multiply the Main Unit by 144. The 3rd,
and **Def. Selling** Unit would be _12-pk_ , which would Multiply the Main Unit by 12.

In this scenario, if you decide you don't want to sell any batteries by the piece
then you would un-check the **Sellable** option on the Main Unit (ea).

```
Here is a screenshot showing this scenario:
```
_Chapter 7: Items_ **181** CA _User Manual_


**_Unit Example 2:_**
For a different example, in the Units of a Service Call Item (below) we've
renamed the original _ea_ Unit to _Local_ and added new Units named _Out of Area_
and _Day_. If you had 4 different price brackets for different distances, then you
could create 4 different units to cover them. This is not the primary usage of
Units, but it is something that can be done with Units.

**Note** : On this Table Control you will need to click the blue + button along the
right side to add a new Unit. If you need to delete a line, select it and click the
red Trash Can button.

**Warning** : When trying to do a major re-structure of Units, such as deleting /
modifying several of them, CA may not allow you to save your changes. If this
happens, try deleting / changing only one thing at a time and saving the Item
after each change.

CA will not allow you to make modifications to the Main Unit other then the
Name, UPC and Sellable. See Beware of Modifying Units (pg 160 ) for more info.

**7.3.6Extras Tab**
Extras are a listing of additional parts / Items that are to appear on an
Invoice / Sales Order each time this Item is sold.

_Extras do not apply to Expense Documents!_
For this example, we will be giving 4 bolts, 4 nuts and 8 washers to our
Customer to use for attaching the Widget. Be sure to double-check that the
correct Unit is selected!

_Chapter 7: Items_ **182** CA _User Manual_


Use the blue + button to add a line
Enter the desired Item in the Item column (see Item Combo Box, page 34 ).
Change the Unit if needed, it will use the Main Unit by default which was
wrong for this setup. Note that this table has the same bug as the Components
table – if the Item or Item Unit field is clicked on, the Unit may change.

Enter the Quantity needed. **Warning** : When the Extra Items are added to an
Invoice, the Quantities listed here are entered. These quantities will not self-
adjust if you modify the quantity of the primary (parent) Item.

We will not be charging our Customer for this hardware, see Sales Tab (pg
198 ) of the **Component Inventory Item** to find out how this is accomplished.

The **Extras** feature could also possibly be used for adding an Alternative Item.
Say you created an Item for a certain OEM part that you stock, and also one for a
quality after-market replacement that you stock. Add the Alternative Item as an
Extra for the OEM Item. Now whenever the OEM part is added to a Sales Order /
Invoice the Alternative Item will be added as well. The Clerk can ask the
Customer which one is preferred, then delete the Item that is not wanted. This
would simplify the Items list for the Clerk, as it would not be necessary to know
the Alternative Part number, just the OEM number.

**7.3.7Taxes Tab**
Under an Item's **Taxes** tab you can set this Item to be **Tax-Exempt** from any
and all **Sales Tax** items in your system.

If the **Exempt** check-box of a Sales Tax line is checked, then this Item will not
be charged that Sales Tax, even if the Customer is taxable.

The list of Sales Taxes should automatically maintain themselves if new taxes
are added, or taxes are removed, etc.

Note that the list will not display inactive Sales Taxes.
There are some special caveats with Taxes and Discounts, see Taxes Tab of (pg
217 ) of Discount Item for more info.

**Update Taxes (button)**
If you made changes to your Sales Tax Items / Structure and it is not
displaying correctly in this screen, click on this button. It should not be
necessary, the Update Taxes routine runs whenever you add or reset a Sales Tax
Item.

_Chapter 7: Items_ **183** CA _User Manual_


**7.3.8Other Tab**
Contains a few general fields. The Other tab is available in all Item Types,
even though not all of the fields apply to all Item Types.

**Notes**
A general purpose field for adding notes regarding this Item. These notes
show on the Item Manager (page 130 ), if the Notes column is set to be visible (see
Table Column Widget, pg 36 ), but do not show on any printouts that this author is
aware of.

**Purchase Alert Note**
Here you can enter a note to be displayed as a pop-up message when you add
this Item to an Expense document (Purchase Order, Vendor Bill).

**Sales Alert Note**
Use this to enter a note to be displayed as a pop-up message when you add
this Item to an Income document (Sales Order, Invoice, etc). The green arrow
buttons between them can be used to quickly copy the text from one Alert Notes
field to the other.

_Chapter 7: Items_ **184** CA _User Manual_


**Item UPC Code**
**_You should enter UPC codes per Item Unit where possible_** - see Units Tab on
page 181. Discount Items do not have Units, therefore this is the only way to add
a UPC to a Discount Item. See Barcode Scanning on page 297 for information on
how barcodes are searched / matched.

**Location**
This is the same Location field that is the Inventory Tab. It allows adding the
Location to Non-Inventory Items.

**Weight**
A field for recording the weight of this Item. If you want this to appear on any
printouts, you will need to have the printout customized. Contact your dealer and
ask about **Printout Customization**.

If you use, or plan to use, weight please read the following carefully.
Only Inventory Item s , Non-Inventory Item s and Asset Item s can have Weight,
you can not add weight to other Item Types, such as Service, Other Charge,
Discount or Sales Tax. Previously the weight field was available on all Item
Types.

The Weight entered for an Item must be for the Item's **Main Unit** (see Proper
use of Units, pg 159 ), weight for all other units is calculated by that Unit's
Multiply / Divide setting. All weight calculations are rounded UP if rounding is
necessary.

Weight is stored in 4 decimal places. There is no “Unit of Weight” setting, all
entries throughout the system are assumed to be the same weight unit, like a
Pound. Most businesses will probably use Pounds as their weight unit, but some
businesses, such as herbalists, may desire to use Ounces or some other smaller
unit for greater accuracy.

The Purchase Order (pg. 240 ) and Invoice (pg. 277 ) screens now have **Weight**
and **Total Wt.** columns in the Line Items table, and a **Total Weight** label display
at the bottom, above and slightly to the left of the Totals labels.

If you use the Measure Quantity field: The Weight column value is calculates
as the selected Unit's Weight multiplied by the Measure Qty. If you do not use
Measure Qty then it is always 1, which will have no effect on the weight
calculation.

If Weight is entered for an Item, it will automatically recall and display on the
document screen. You can also manually edit the Weight field, the Total Wt will
automatically calculate as Weight x Quantity. If you attempt to add Weight to a
Line Item and it just reverts to **0** then it is because that line's Item does not
support Weight.

_Chapter 7: Items_ **185** CA _User Manual_


**7.3.9History Tab**
Lists documents containing this item. There are filters at top for document
type and status.

Double-click on a table row or use the Open button (above list) to Open the
document. Ctrl+Click on a row to open the document Print Preview.

_Chapter 7: Items_ **186** CA _User Manual_


### 7.4 Non-Inventory Item.........................................................................................

This is the standard item type to use for all the 'widgets', 'items',
'thingamajigs' and 'doohickeys' you sell. They should be physical items, things
you can see, touch, etc. Here are multiple shots showing the setup of a "Green
Widget". The different pictures are just showing different **tabs** of the same Item.

**7.4.1General Fields**

**Item Number**
Along the top are fields for the **Item Number** , enter an easy-to-remember and
descriptive, but fairly short part number here.

It is a good idea to create a "Naming Convention" for your Item Numbers. In
the sample shown here the item number starts with wgt, which is an abbreviation
for "widget". If you apply the same starting letters to all similar items, then you
can type in the known letters ( _wgt_ ) and the **Item Combo Box** will supply a list of
all available Items of this family (wgtGreen, wgtBlue, wgtRed, etc.). If you create
special Items to use only in Expense documents, you might name all of them
starting with _exp_ , for example; expAdvertising, expFuel, expPhone, expOffice, etc.

_Chapter 7: Items_ **187** CA _User Manual_


A good practice is to use the Brand for a naming convention, such as starting all
Energizer products with a code such as _ener_. **Note** : for a description of how the
Item Widget works, see Item Combo Box (page 34 ).

**Item Name**
The next field is **Item Name**. This is somewhat redundant, but there are
times when it can be useful. For example, if several items have a similar item
number, a more descriptive Item Name can be used to enable the user to easily
differentiate between them in the Item List. This field is optional.

In the **Item Combo Boxes** throughout the system, the item will display as the
Item Number followed by a space followed by the Item Name: " _wgtGRN Green
Widget_ " for the sample given.

**Inventory Group**
This setting is optional, it is used to group items of similar type or department
together for easier reporting and searching. See Inventory Groups on page 130
for list setup.

**7.4.2Change To Inventory**
This button, located along the bottom, to the right of the Prev / Next buttons,
appears only for Non-Inventory items. Clicking this will convert the current Non-
Inventory Item into an Inventory Item.

This feature documented in Converting Non-Inventory to Inventory on page
192

```
7.4.3Sales Tab
See Sales Tab on page 177.
```
**7.4.4Purchases Tab**
Now we will switch to
the **Purchases tab**.
These are settings that
are applied when this
Item is Purchased
(Expense Zone).

**Purchase
Description**
This is what displays
on the PO printout as the
full description of the
Item. This field accepts

_Chapter 7: Items_ **188** CA _User Manual_


up to 500 characters of text. This can also be entered / modified on a per
document basis. This field may be left blank in any one of the following
conditions:

1. This is not an Item that you buy.
2. The purchase description is different each time you buy this item.
3. The Purchase Description is same as the Sales Description

**Preferred Vendor**
Below the Purchase Description is the **Preferred Vendor** where you can
choose which Vendor you normally buy this Item from. This Vendor will display
on the Reorder Report.

**Vendor's Part Number**
An Optional field to enter the Part Number to be displayed (printed) on the PO
and Vendor Bill instead of the Item Number you assigned it at top of the form.

Your Vendor might have an entirely different Item Number for a product then
what you are using. _Example:_ Your Item Number _"bolt 3/8x2.5"_ might be Item
Number _"NRLB038250"_ in your Vendor's system.

If the Vendor's Part Number field is blank, then your Item Number will be used
on POs.

**Purchase/COGS Account**
The **Purchase/COGS Account** is the GL Account that the system will use
whenever this Item appears on an **Expense** document. That LINK again!

See the COGS vs. Expense (page 92 ) if you don't know if this Item is a COGS
or an Expense.

For this Item we have set it to _5000 Purchases - Inventory_. This is the default
COGS account that is in the initial GL Account list.

For different settings of this field, see the Purchases Tab of the Component
Inventory Item and the Purchases Tab of the Manufactured Inventory Item.

This account keeps tab of how much money you spend on all the Items that are
linked to this particular COGS Account. The P&L will show the total spend in a
specific Period of Time.

**Item Cost**
This field is exact same as the one on the Sales Tab, and they will always be
same. Changing one will change the other. Cost can have up to 8 decimal places.

**Average Cost**
The **Average Cost** is a calculated field (you can't modify it) that is used for
Inventory Items. It shows the calculated average per Item cost of the Items
currently in stock.

_Chapter 7: Items_ **189** CA _User Manual_


When you sell an Inventory Item, this is the amount that is used for the
**Inventory Variance** adjustment.

If you feel this number is not correct, try running the Recalc Avg Cost &
Pricing utility (pg 135 ) that is in the Items Menu.

```
This field can utilize up to 8 decimal places.
```
**Update Cost from Purchases**
If this is checked, then the Item Cost field will update itself each time you
purchase the item at a different cost from the cost then is displayed now.

This is a nice feature, but think about it for each Item and be sure you want it
checked. For Items that are frequently purchased and have a rapidly fluctuating
cost you may want this unchecked, to prevent the Selling Price from bouncing up
and down with the Cost. It would not be a good thing to have a customer bring an
Item to the counter that is marked $14.95 and have CA put $16.25 on the Invoice.

```
7.4.5Units Tab
See Units Tab on page 181.
```
**UPC Field**
If you use Barcode Scanning (pg 297 ) enter the UPC (bar)code per each Item
Unit.

```
7.4.6Extras Tab
See Extras Tab on page 182.
```
```
7.4.7Taxes Tab
See Taxes Tab on page 183.
```
**7.4.8Other Tab**

The Other Tab is covered in the Retail Inventory Item section (page 197 ).

**7.4.9Item History Tab**

See History Tab on page 186.

_Chapter 7: Items_ **190** CA _User Manual_


### 7.5 Inventory Item.................................................................................................

There is a setting to enable / disable **Inventory Items**. On a new database
Inventory Items are disabled, if you wish to be able to add new Inventory Items to
CA you need to enable this setting. Menu > Items > Item Settings > Inventory
tab > **Enable Inventory Items**.

This Item Type is used only if you are tracking inventory. You should not use
Inventory items unless you understand how it works, and are willing to commit
the necessary time to stay on top of your inventory and make the necessary
adjustments to keep the system in sync.

Inventory Tracking is quite complex. In a Retail Sales business inventory
tracking is doable, but in a Manufacturing business it can be quite difficult to
keep the system's inventory counts and financial reports accurate.

If you use Inventory Items to track raw materials such as roll or sheet stock
that is cut into smaller pieces, with waste material resulting from the cutting,
then you will need to do frequent (weekly or monthly?) inventory counts, and
make Inventory Adjustments in CA to keep the CA **Qty on Hand** ( **QOH** ) correct.
Otherwise the QOH in CA will drift off to the point that it is quite useless.

```
The advantage of using Inventory Items is 2-fold:
```
1. It allows you to see at an instant if you have the necessary QOH to make a
sale. If you enter an Inventory Item on a document, it will display the current
QOH for you to see.
2. It provides a more accurate P&L. Inventory Items do not show up as a
COGS until they are Sold. Making a large purchase of Inventory will not make
your P&L show a loss, as it would if you were to make the same purchase using
Non-Inventory Items. Doing an extra-high volume of sales for a particular period
will not create an extreme profit when using Inventory Items, only the profit
realized on the Items sold will show on the P&L.

**We will be creating 3 different sample Inventory Items here:**

- A Retail Inventory Item (page 193 ) is an item that is Purchased and Re-Sold
    as-is.
- A Component Inventory Item (page 198 ) is something you won't be selling
    to your customers directly but use in manufacturing other Items.
- A Manufactured Inventory Item (page 202 ) is a combination of a multiple
    Component Inventory Items and/or other Items, something you manufacture
    in-house and sell to your customers.
Note: The 3 'different' Inventory Items listed above are are all identical in CA,
there is only one Item Type for Inventory Items. It is just the way the Items are
used that is different.

If you are doing manufacturing and using CA to track your Inventory, you will
need to use the Manufacturing process (page 225 ) to keep your inventory up to
date.

_Chapter 7: Items_ **191** CA _User Manual_


**Warning** : VPWR reports that they've encountered incorrect inventory count
figures that they traced down to this particular sequence of events:

1. User A opened an Item to edit it, then for whatever reason did close the
form right away.
2. User B (on a different machine) created an Invoice or Sales Receipt and sold
1 or more of the Item that User A was editing. _This updated the inventory count
in the database._
3. User A came back to the Item Edit, closed and saved the Items form. _This
re-wrote the database with the Inventory Count that the Item had when User A
opened it, undoing the changes made by User B!_

**Avoid this Problem:** Don't leave an Item or Document in and Edit form and
walk away!

**7.5.1Converting Non-Inventory to Inventory**
This feature allows you to convert existing Non-Inventory items to Inventory
items. See Inventory vs. Non-Inventory on pg 169. Text added v2024.1

You can convert individual items from the Item Edit screen, see Change To
Inventory (pg 188 ) or do conversions on multiple items at once through the
Convert to Inventory Item utility (pg 136 ).

When you convert an item it will set the new Item's Asset Account and
Variance Account to the GL Accounts are currently filled in Item Settings (pg
132 ). If these settings are not filled in then the conversion will fail.

When doing bulk conversions you will also be asked if you want to set the Qty
On Hand to Zero or set to a value based on existing history of the item. If you
choose the latter option an Inventory Adjustment will be created, which will use
the item's **Variance GL** as the adjustment's GL Account in order to offset the
original purchase of the item.

**Legal Disclaimer:** This feature was added per user request, but likely should
not have been. Converting a Non-Inventory item to an Inventory Item is not
standard accounting practice. The conversion process will generate a Journal
Entry that can create skewed P&L numbers for the period in which it was done.

**Warning** : This is not reversible – there is no way to convert an Inventory Item
into a Non-Inventory Item.

**Warning:** If you edit and re-save a document where a converted Item was
previously used as a non-inventory item, it will now treat it as an Inventory item
and will change your financial history. **Use this feature at your own risk!**

_Chapter 7: Items_ **192** CA _User Manual_


### 7.6 Retail Inventory Item......................................................................................

A Retail Item is the easiest Inventory Item to track. This is an Item that you
purchase from a Vendor, then turn around and sell it to your Customer, still in the
same condition / form as it was when you bought it.

For our example we'll say we're in the business of making Widgets, but we
found that Millcreek Machine makes a Blue Widget at a price that we can't
compete with, so we buy Blue Widgets from Millcreek in case lots of 24 pieces
and sell them, one piece at a time, to our customers.

```
7.6.1General Fields
These are same as the General Fields of a Non-Inventory Item (page 187 ).
The Inventory Group is still Optional, even though this is an Inventory Item.
```
```
7.6.2Sales Tab
This is just like the Sales Tab of a Non-Inventory Item (page 188 ).
```
**Sales Account**
For the Sales Account (GL Income Account) we decided to track Purchased
Goods and Manufactured Goods in different GL Accounts.

_Chapter 7: Items_ **193** CA _User Manual_


We modified the default GL Account _4000 Sales_ to read _4000 Sales -
Purchased Goods_ so that we can easily distinguish it from the new Income
Account we created, _4002 Sales - Manufactured Goods_. See General Ledger
Menu (page 126 ) for help.

**Item Cost**
Because we purchase Blue Widgets in cases of 24, we set the _case_ Unit to be
the Main Unit, so the Item Cost of 959.23 is for a _case_ of Blue Widgets. If you
look at the Price Levels you can see that the Retail Selling Price for a single ( _ea_ )
Blue Widget is 59.95.

**Warning** : This text is incorrect, the Main Unit should always be _ea_. CA will
allow up to 8 decimal places in Cost / Price and Average Cost fields, which should
minimize the rounding errors.

**Price Levels**
Here you will see we've created units labeled _case_ and _ea_. This is done in the
Units Tab. This allows fine control of the Selling Price. When we add this Item to
an Invoice (to sell it) the Rate (Selling Price) will depend on if the Customer is set
for _Retail_ or _Wholesale_ , and also which Unit is selected for that line, _ea_ or case.

**7.6.3Purchases Tab**
Again, this looks and acts same as a Non-Inventory Item's Purchases Tab (page
188 ).

_Chapter 7: Items_ **194** CA _User Manual_


**Purchase/COGS Account**
This is set to _5000 Purchases - Inventory_.
For an Inventory Item, this should always be a COGS Account, never be an
Expense Account.

See Purchases Tab (page 199 ) of Component Inventory Item and Purchases
Tab (page 202 ) of Manufactured Inventory Item.

```
7.6.4Units Tab
Units can be used to split case quantities into individual retail units.
See Units on page 156 for details.
```
**7.6.5Inventory Tab**
This tab has settings for the GL Accounts that are used for Tracking Inventory
(page 104 )

**Asset Account**
This is the GL Account that tracks the current value of all Inventory On Hand.
Each time this Item is purchased, it Adds the cost of the Item(s) to this GL
Account.

Each time this Item is sold, it Subtracts the Average Cost (page 189 ) of this
Item from this GL Account.

**Inventory Variance**
This is the COGS Variance Account that is used to adjust the COGS section of
your P&L Report.

Each time this Item is purchased, it Subtracts the cost of the Item(s) from this
GL Account to offset the COGS Purchase Account entry that was made.

Each time this Item is sold, it Adds the Average Cost (page 189 ) of this Item to
this GL Account, to create a Cost of Goods Sold for the sale.

_Chapter 7: Items_ **195** CA _User Manual_


**Location**
This is an optional Text Field that you can use to store information such as the
Bin Number where this Item is stored. This sample entry is supposed to mean
Isle E, Shelf 2, Bin 8. Each business that uses Location will probably have their
own implementation of its format.

**Qty On Hand**
This is a Calculated Field, it shows the quantity of this Item that is currently in
stock. This number operates on the Main Unit, 1.6 cases means we have 28
pieces on hand!

**Qty On PO**
This field displays how many (main unit) of this Item are currently on Purchase
Orders, and not received yet.

**Qty On SO**
This field displays how many (Main Unit) of this Item are currently on Sales
Orders, and not Invoiced yet.

**Order Min**
Optional field to enter the Minimum qty (Main Unit) you should purchase at
one time.

**Order Max**
Optional field to enter the Maximum qty (Main Unit) you should purchase at
one time.

Order Min and Order Max are printed on the **Reorder Report** , but they do not
affect or control anything when you place an order.

**Alert Level**
Optional field to to enter at what point this Item should be reordered.
Once the Qty on Hand drops to or below the Alert Level, then the **Item Stock
Status** Report will show a _Yes_ in the Order column.

The Alert Level setting will not notify you that the Item is running low on
stock, you will need to view the **Item Stock Status** Report to see which Items
should be ordered.

**7.6.6Components Tab**
A Resale Item usually does not have any components. Usage of Components
Tab (page 204 ) is covered in the **Manufactured Inventory Item** section.

_Chapter 7: Items_ **196** CA _User Manual_


```
7.6.7Extras Tab
See Extras Tab on page 182 for details.
```
**7.6.8Taxes Tab**
We have left all Taxes unchecked, this Item is not Exempt from Sales Tax.
See the Taxes Tab (page 210 ) of the Service Item for more details on Sales
Taxes.

```
7.6.9Other Tab
See Other Tab on page 184.
```
_Chapter 7: Items_ **197** CA _User Manual_


### 7.7 Component Inventory Item.............................................................................

There is no separate Item Type for Components vs. Retail or Manufactured
Inventory Items, but each one is distinct because of what it will be used for.

A Component is something you are not likely to sell to your Customer by itself,
but as a portion of some other (Manufactured) Item.

See Retail Inventory Item (page 193 ) and Manufactured Inventory Item (page
202 ) for more details on Inventory Items.

The first example Item here is a 3/8" x 2-1/2" bolt that is used in
manufacturing Widgets. We also hand out a set of these bolts to our customers
whenever we sell a Blue Widget, see Extras Tab (pg 182 ).

There are, naturally, also Items for a matching nut and washer. Their setup is
identical to the bolt except for the Numbers and Descriptions.

**7.7.1Sales Tab**

**Sales Account**
When this Item is sold, we're using the Purchased Goods sales account,
although this particular item will seldom be sold for a charge, so it will not show
up as an Income, but it will still display a Cost of Goods Sold if it is listed on an
Invoice for $0.00.

_Chapter 7: Items_ **198** CA _User Manual_


**Price Levels / Markup**
We want to give these bolts to our Retail Customer at no charge. To do this,
we just set the **Formula** for the _ea_ Unit to 0 (the Number 0, not the letter O) for
the _Retail Price_ Level. Now when a bolt is added to the Invoice of a Retail
Customer, the price will be $0.00.

**Warning** : If you provide Inventory Items to your Customers for free, you still
need to add it as a Line Item on the Invoice, so that it will deduct from your
Inventory Quantity On Hand.

**7.7.2Purchases Tab**

The only setting here that is notably different from the Purchases Tab (page
188 ) of the Non-Inventory Item is the COGS Account.

The GL Account for purchases of an Inventory Item is always a COGS Account,
never an Expense Account.

We have created a GL COGS Account _5012 Purchases - Hardware_ to use for all
hardware type purchases. This allows easily keeping an eye on how much of our
money goes into Hardware vs. Material (raw stock) and Inventory Goods (such as
Blue Widgets).

```
7.7.3Units Tab
See Units Tab (pg 181 ) for general info.
```
_Chapter 7: Items_ **199** CA _User Manual_


Here we have the Main Unit as as _ea_ (per bolt) with the _box_ Unit multiplying
the Main Unit by 50 (a box of 50 pc). Note that the Def. Purchasing is set to _box_ ,
you always buy them by the box, not per each.

Note that we have entered a **UPC** code, which can be used to place the Item
on a PO with a barcode scanner. Of course this only works if your products have
labels with a Barcode to scan, and it must match the UPC here!

**7.7.4Inventory Tab**
These settings are explained in the Inventory Tab (page 195 ) of the Retail
Inventory Item. The settings that are different here is the GL Accounts.

We've created an Asset Account for hardware, as well as a Variance Account
for hardware.0

GL Accounts for Inventory Items should be thought of as a set, Asset,
Purchase, Variance and Income.

```
For help with the Components Tab (page 204 ) see Mfg. Inventory Item.
All other tabs, see Retail Inventory Item (page 193 ).
```
**7.7.5Raw Materials**

Here is another Component - this is a Raw Material Item, some mild steel L
braces we buy from _America's Best Metals_ in 8' sections. This is shown here so

_Chapter 7: Items_ **200** CA _User Manual_


you can understand the following Items.

```
Note that we're using the Material GL Accounts for the Inventory section.
```
_Chapter 7: Items_ **201** CA _User Manual_


### 7.8 Manufactured Inventory Item.........................................................................

Here we will be exploring the final section of Inventory Items, the Components
Tab. A Manufactured Item contains Components, it is made up (in-house) of
multiple other Items of any type.

We will first go through all the pertaining Tabs of a 3-1/2 ft. L brace that we're
making as part of our Orange Widget project.

The brace is made of 8 ft. stock, we can make 2 of these braces from each
piece. See Raw Materials on page 200 for setup of this stock material.

At the end we will show the Components Tab of the Orange Widget, which
contains 2 of these braces, besides some other parts

**7.8.1Sales Tab**

This is pretty much like the Sales Tab (page 188 ) of a Non-Inventory Item.
The difference is the Sales Account, which we've set to _4002 Sales - Mfg
Goods_. This is a GL Account we created to track the sales of goods that we make
in-house.

**7.8.2Purchases Tab**
The only setting here that is notably different from the Purchases Tab (page
188 ) of the Non-Inventory Item is the COGS Account.

**Purchase/COGS Account**
The GL Account for purchases of an Inventory Item is always a COGS Account,
never an Expense Account.

```
We have created a GL COGS Account 5010 Purchases - Material to use for all
```
_Chapter 7: Items_ **202** CA _User Manual_


raw material purchases except Hardware, see the Purchases Tab (page 199 ) of
Component Inventory Item.

Using this separate account allows easily keeping an eye on how much of your
money goes into material vs. Inventory Goods (such as Blue Widgets, see Retail
Inventory Item on page 193 ).

Since this part is made in-shop and not purchased, this Purchase Account
should never be used. It is still best to make sure this account setting is correct
in case you decide to have a batch made by a sub-contractor.

**Item Cost**
The Item Cost field for this Item is not a price that is entered, it is determined
by the Components it contains, see Components Tab.

The Remaining Purchase fields are blank, as they don't apply to a
manufactured Item.

**7.8.3Inventory Tab**

Here we are using the _Material_ Asset and Variance accounts. Even though
this is something we are making, it is still not a complete Widget that we sell to a
Customer, but a portion of one, so it is classified as Material rather then Inventory
(Goods to sell).

_Chapter 7: Items_ **203** CA _User Manual_


We've entered some numbers int the Order Min / Max fields to use as a
guideline for how big a batch we should make at a time.

**7.8.4Components Tab**
The **Components** are the sub-parts (Items) that are used to make this Item.
For this brace we are cutting an 8 foot length of stock into 2 pieces of 3-1/2 ft.
length. The remaining 1 ft. of material is discarded as waste, so for our purpose
it takes 1/2 (.5) of one piece of this stock to make a brace. There are also some
holes drilled into it, etc.

**Warning** : It's possible to add the **labor** to the Components list (using a
Service Item, page 208 ) and have the labor cost figured in as part of the cost of
the piece. This poses a problem... When the Item is **Manufactured** , then this
labor gets added to COGS on the P&L Report. When you pay your employees
their wages at a later date (payroll), then the same labor gets added to your
COGS again, giving you a false COGS number on your P&L. There is a setting
that allows you to enter Non-Inventory and Labor components to calculate the
cost, but not have them generate any entries when the Item is Manufactured. See
Mfg Cost based on Components, page 134.

**Item Components**
This is the Table Control where you enter the Components, the individual
pieces which are used to make this Item.

Note that you will need to add the first row to the table using the blue **+**
button along the right side.

```
Here are the columns available in this table.
```
**_Item_**
Here you select an Item
that you have already
entered in CA. Note that you
may not add the Item to itself
as a Component, if you do
you will get the error
message shown here when you try to save.

**_Item Description_**
Shows the selected Item's Sales Description – so you can see what you
selected. The Item Description is editable, so you can customize what appears on
the Manufacturing document. **Special Note:** If you customize the text, it will

_Chapter 7: Items_ **204** CA _User Manual_


remain that way. If you leave the text as it appeared, then it will update itself if
you update the Sales Description of that Item.

**_Item Unit_**
Double-check and make corrections here if needed. It will automatically set
the Main Unit here, which is not always what is wanted.

**_Unit Cost_**
This is a Lookup, you can't modify it. It displays the cost of 1 of this item, of
the unit selected. This is Cost, not Selling Price!

**_Qty_**
Enter the quantity of this component required. This number can be a decimal
partial number, as displayed here.

```
Total
This is the Total Cost – Unit Cost x Qty. Read-Only.
```
**Base Item Cost On Component Cost**
This check-box at the bottom of the form controls if you allow the cost of the
components determine the cost of the Item or not. If you un-check this, then you
can manually modify the Cost field in the Sales / Purchases tab. If you leave this
checked, then whenever the Cost of any of the components changes, that change
will be reflected in the Cost of the Item the next time you Manufacture it.

**Total Cost**
This is a Calculated Field showing you the total cost of all the components
listed, using the units and quantities entered.

_Chapter 7: Items_ **205** CA _User Manual_


See the Manufacturing section (page 225 ) for 'building', or 'manufacturing'
this Item.

```
The Extras Tab is covered in the Retail Inventory Item section (page 197 ).
```
The Taxes Tab is covered in the Service Item section (page 210 ). The Other
Tab is covered in the Retail Inventory Item section (page 197 ).

Following is the **Components** Tab of another item, an 'Orange Widget' that
contains 6 of the braces we were making an Item for.

We are using a 'Red Widget' as the base, and adding a set of roller bearings
and seals, some Stainless Steel roll stock, braces, bolts, nuts, washers, etc.

The Orange Widget is a fictional Item, as I wouldn't want to expose trade
secrets. We'd also need some Orange paint in here somewhere, it would seem to
me.

_Chapter 7: Items_ **206** CA _User Manual_


**7.8.5Import Components**
When entering item components sometimes it's faster to modify the
component list of another item rather than manually enter each component.

By clicking the **Import** button below the component you can import the list of
components from any other item into this item's component list.

If there is already a list of components present when you import it will allow
you to choose whether to replace the existing list or add to it.

_Chapter 7: Items_ **207** CA _User Manual_


### 7.9 Service Item....................................................................................................

This type is for services (labor) charges that you Invoice your your customers
for, such as Repairs, Service Call, Tech Support, etc.

In the following screenshots we will be creating an Item called _Service Call_ ,
used for charging our customer a fee for doing an on-site installation of a product.

We will be using the Units to create 2 separate Rates for _Local_ and _Out of
Area_. The Retail Inventory Item's Units Tab (page 195 ) shows a different usage of
Units.

See Non-Inventory Item (page 187 ) for help with the basic setup. We will
explain here only the fields and settings that are different.

**7.9.1Sales Tab**

```
Sales Account
```
In this example the Sales Account is set to an Income Account _4010 Service_.
The reason for not using the _4000 Sales_ account is so that all Income from
services (labor) is shown as a separate line item on the Profit & Loss Report. The
_4010 Service_ GL Account was not part of the default setup, it was added for this
purpose.

If you don't don't want this to show as separate lines, it is perfectly fine to use
the _4000 Sales_ account, as it will probably not make any difference on your
Income Tax Return.

_Chapter 7: Items_ **208** CA _User Manual_


**Item Cost and Markup Formula**
As displayed here, we've entered a 'Cost' of 30.00 as a base to work with. The
Markup Formula is adding 50% to this to obtain a Selling Price of 45.00.

**_Price Levels_**
Here's where things get a little more complicated. This previous screenshot
was taken after more **Units** were added, see Units on page 156.

For each Unit of the Item, there is one line for each Price Level. Note: The
number of Price Levels (page 130 ) might be completely different. Maybe you
have only one Price Level, or maybe you have 6.

The Markup Formula for each line is set to generate an appropriate Selling
Price for that Price Level / Unit combination. In all instances the _Cost_ is 30.00,
the number entered in the Item Cost field.

If you want to do a **price increase** at a later date, you just increase the Cost
and all the fields will be recalculated - the price difference between the different
Price Levels / Units combinations remains proportionally same.

You can also use fixed numbers in the Markup Formulas instead of
percentages, to set a price $15 more then cost, use the formula _Cost + 15_. The
formulas can be quite complex, see Markup Formulas on page 162.

**7.9.2Purchases Tab**

I've decided to set up this item so it can also be used on a Vendor Bill, when
someone charges us for a Service Call (to repair the air compressor, for example).

**Purchase/COGS Account**
This is linked to the _6650 Repairs & Maintenance_ Expense Account. With this
setting you would not want to use this Item to enter a Contracted Labor charge,
which is a COGS Account.

_Chapter 7: Items_ **209** CA _User Manual_


**Item Cost**
The Cost is really not a part of the Purchase end of this Item, but if you set this
to 0 then all your Selling Prices will 0 as well, which would not be desirable for
the intended purpose of this Item. When you enter this Item on a Vendor Bill it
will enter this Cost, and you will need to adjust it to whatever the actual amount
is on the Vendor's Bill. In this case, be sure to un-check the **Update Cost from
Purchases**!

**7.9.3Units Tab**

See Units on page 156.

**7.9.4Taxes Tab**

See Taxes Tab on page 183.

```
The Other Tab is covered in the Retail Inventory Item section (page 197 ).
```
_Chapter 7: Items_ **210** CA _User Manual_


### 7.10 Other Charge Item........................................................................................

Use this type for items that don't nicely fit in any other category. Displayed
here is a Finance Charge Item (page 302 ), which you will probably need to create.
In the Finance Charge Item the Cost field is left 0.00, as the Price is always a
custom price that is calculated by the Assess Finance Charges form (page 302 ).

```
All the settings are similar the Non-Inventory Item, see page 187.
```
On the Purchases tab the Purchase/COGS Account is set to an **Interest
Expense** account. This allows the same Item that you use to Invoice your
Customers for late fees to also be used for Interest Fees on loans, etc (Vendor
Bills).

_Chapter 7: Items_ **211** CA _User Manual_


### 7.11 Sales Tax Item...............................................................................................

CA tracks Sales Tax for you. It is required to have at least one Sales Tax Item,
even if you never charge Sales Tax. The system will not function without it, and it
should be one of the very first steps in setting up CA. Creating a new database
with CA will automatically created a Sales Tax Item, but you will need to
customize the Code / Description / Rate. Shown is a setup for Homes County
(Ohio) Sales Tax with a rate of 7.00%

The **Item Number** and **Item Name** are same as explained for the Non-
Inventory Item (page 187 ).

```
Code
The text that is displayed throughout the system as the Tax Region.
```
**Tax Liability Account**
Should be the GL Account _2200 Sales Tax Payable_ which is nicely set up for
you by default. Notice that Sales Tax only has 1 GL Account to link to.

```
Tax Rate
This is the percentage of the tax. 7.25 = 7.25%
```
**Tax Agency**
This is a link to a Vendor in CA, the one you pay your Sales Tax to. You must
create this Vendor before you can create the Sales Tax Item.

```
Geographic Area
Is the State or Province you are located in.
No field in the Sales Tax tab may be left blank!
```
_Chapter 7: Items_ **212** CA _User Manual_


The **Units** tab is available, but doesn't really apply to Sales Taxes.
The **Default Exempt** settings allow selecting whether this Tax is set as
Exempt or not when creating new Items or Customers.

If your business is largely to non-taxable customers you should check the **Is
Default Exempt for Customers** option so new customers added to the system
are non-taxable by default (uncheck the Tax Exempt option on Customers that are
not tax exempt).

If you are in the food service business where most items are never taxable you
can use the **Is Default Exempt for Items** option to make new items non-taxable
by default.

**7.11.2 Tax Exemption**
If your state requires you to track your exempt taxes in different categories,
you may need to create a different Sales Tax Item for each category of exemption
(Farm, Resale, etc.), each with a Rate of 0.00. This allows you to generate a
**Sales Tax Liability** Report of sales for each different exemption type.

You need to do this only if your state requires that you break up your non-
taxable sales into more then one category.

See Collecting multiple Sales Taxes15.1.3 on page 379.
**The way Exempt Sales are handled within CA is something that could
possibly change in the future, if enough people make requests to Classic
Word Processors.** (Developer note: As of version 2019.1 this is on the "To Do" list, but might
not be in the immediate future.)

```
The Other Tab is covered in the Retail Inventory Item section, see page 197.
```
_Chapter 7: Items_ **213** CA _User Manual_


### 7.12 Discount Item................................................................................................

Discount Items are used to apply a Discount, usually to Subtract from a
document's total instead of Adding to the total. You must enter a Negative Rate
to create a Discount, if you enter a positive number in Rate it will Add to total,
which can be useful for some purposes (like adding a 2% Processing fee).

**Item Number** , **Item Name** and **Inventory Group** are same as all other types
of Items.

**7.12.1 Discount Tab**

**Description**
This is what shows up as the line item description on the Invoice when it is
used.

**Sales Account**
A **Sales Discount** given to your Customer is a Deduction of Income. The
Sales Account is set to an Income Account _4800 Sales Discounts_ (which is a
default GL Account for this purpose).

Because a Discount is a deduction (negative number) it will show a negative
number on your P&L, which will subtract from the Income received.

If you sell an Item for $500 and apply a 10% Discount, with a Discount Item,
your P&L will show $500 in the Sales (Income) Account that is linked to that

_Chapter 7: Items_ **214** CA _User Manual_


particular Item, and -$50 in the Sales Discount (Income) Account.

**Notice** : It is also permissible to set the Sales Account to a COGS GL Account,
which increases your Cost of Goods Sold rather then Deducting your Income. You
should talk to your Accountant to find out which is the correct method for you.

**Purchase Account**
There is no default GL Account that fits nicely for the Purchase Account. You
would seldom add a Discount Item to an Expense document, and if you do you
should know what you are doing and why you are doing so, which would lead to
the answer as to what GL Account this setting should be.

**Remember, the Purchase Account setting controls which GL Account
will be used when this Item is used on an Expense document (Vendor Bill).**

If you receive a discount from a Vendor the preferred way of handling it is to
deduct the discount from the cost of each line item as you enter the Bill, in order
that the discount reduces the appropriate Expense or COGS Account.

Alternatively, you could use the Discount Item to reduce the amount of your
Sales Discounts that you give by setting the Purchase Account same as the Sales
Account.

Or you can set the Purchase Account to an Expense or COGS Account, which
would then Reduce that category total. OK, you had better talk to your
Accountant to find out how he/she is handling this, then do the same. An
important thing is to be consistent, don't do some discounts one way and other
another way.

In the Pay Bills (page 256 ) you'll find how to handle a Prompt Payment
Discount that a Vendor gives you.

**Rate Type**
A discount Item can be either **Percent** based or **Fixed** rate.
When a Discount Items has a **Fixed** rate type then it acts just like other items.
You enter the amount of the Discount (as a negative number) in the Rate field
(this can be changed on the document itself).

When a Discount Item is set as **Percent** rate type then it calculates the Total
as a percentage of the total of document lines ABOVE the Discount Item. The
Item has settings on how it handles other discount items it encounters, or to limit
it to only a single item.

**Rate**
This is a number determining the amount of discount. Note: To create a
discount (negative number) you will need to make this number negative, by
adding a minus in front of the number, like this: -10 for a 10% discount. For a
Fixed Rate Type just enter the $ amount, like -5.00 for a $5.00 discount.

```
Starting version 2023.1 it is permitted to save the item with a Rate of 0.00.
```
_Chapter 7: Items_ **215** CA _User Manual_


```
Percent Discount Functionality
This controls how Percent based discounts calculate.
```
**_Apply To:_**
Determines which lines this discount applies to. There are exceptions, based
on If Discounted setting, see next section.

- **ALL_ITEMS** (the default value): Calculates on total of all rows above
    this Discount Item
- **ONLY_LAST_ITEM** : As implied, this calculates the discount amount
    only for the line item immediately above this discount item.
- **ONLY_INVENTORY_GROUP** : Only calculates the discount on items
    that belong to the same **Inventory Group** as this Discount Item does.
    See Inventory Groups on pg 130.

**_If Discounted:_**
Controls how it handles items that have already been discounted by another
Discount Item, to prevent double-discounting, etc.

- **SKIP** (the default value): If an Item already has a discount applied then it
    does not include it when calculating the discount amount.
- **PRICE_BEFORE_DISCOUNT** : Calculates discount on the original total of
    the line, even if it has been discounted before. Say you have do 20% off a
    single item that has a line total of $100, then later add a 10% on all items
    (with PRICE_BEFORE_DISCOUNT), then the total discount on that item that
    was previously discounted will be 30%, for a final price of $70.
- **PRICE_AFTER_DISCOUNT** : Calculates the discount on the total of the
    line after the other discount(s) has been taken off. If you do a 20% discount
    on a single item with a line total of $100 before discount (discount = $20)
    then do a 10% discount on all items (with PRICE_AFTER_DISCOUNT) it will
    calculate 10% of $80 = $8.00, for a final price of $72 for the double-
    discounted item.
- **GREATER_DISCOUNT** : Uses only the greatest of all discounts applied to a
    line. In the case of 20% and 10% discounts being applied as in previous
    examples the 10% discount will skip this line because the 20% discount
    already applied is more then 10%. In the even that the first discount
    applied was 10% and you then apply a 20% discount that is set to
    GREATER_DISCOUNT the second discount will also calculate as 10%, for a
    total of 20%.

**_Apply To All (Stay @ Bottom)_**
This setting is to be used when the discount is to be applied to the entire
document, like in a store-wide 10% Sale. If this option is checked the Discount
Item line 'floats' and stays at the bottom of the document, immediately above the
Sales Tax line(s).

_Chapter 7: Items_ **216** CA _User Manual_


```
7.12.2 Taxes Tab
See the Taxes Tab on page 183 for general information.
How does Sales Tax apply to Discounts? It's quite important, actually.
```
**If you sell a Taxable Item for $500 and apply a Discount of 10% ($50)
then...**

If the Discount Item is also Taxable it will reduce the amount of tax you collect,
as it will create a negative Sales Tax amount for the Discount Item. In effect, your
Customer will pay Sales Tax on only $450. This is the way it is normally be
handled.

If the Discount Item is Not Taxable, your Customer will pay Sales Tax on the
full $500. It is possible that some state(s) would have laws concerning this. No
such laws exists to the knowledge of this author, but this author is not an
Accountant so you'd better talk to your yours.

**Warning** : A sticky situation can occur if you sell a Non-Taxable Item to a
Taxable Customer, and then apply a Taxable Discount. This creates a Negative
Sales Tax amount and apply it to your document. If this happens you will need to
un-check the Tax on the Discount line (in Invoice) to remove the negative tax.

**7.12.3 Other Tab**
The Other Tab is covered in the Retail Inventory Item section (page 197 ).
In version 2023.1 a bug was fixed that had previously prevented codes entered
in the Item UPC Code field (pg 185 ) on this tab to be picked up by the barcode
scanning process.

_Chapter 7: Items_ **217** CA _User Manual_


### 7.13 Asset Item.....................................................................................................

This type of item is used to link to Asset accounts. For this example we
created an Asset Item named _asstMachinery_.

We will be using this (sample) Item to buy and dispose machinery and other
major equipment for our business. Be sure to read this entire Asset Item section
carefully to understand how it works.

You would also use an Asset Item if you want to, for some reason, create an
Item for a Bank Account.

**7.13.1 Asset Tab**
For this sample we've
created an Asset Item
named _asstMachinery_ to
use when equipment is
purchased or disposed.

**Asset Account**
An Asset Item has only
1 GL Account link, for an
Asset Account. With this
setup it has rather limited
usage, which we will
attempt to explain.

**Both purchases (Expense Documents) and sales (Income Documents)
link to this same Asset Account.**

The default GL Account is _1300 Inventory Asset_. He we changed this to _1500
Furniture & Equipment_ , which is also a default (ready-made) GL Account,
because we're using this Item to purchase Equipment, not Inventory.

**Asset Count**
This is a calculated (non-editable) number showing the quantity of this Item
purchased, less the quantity sold. Likely someone uses this for a purpose, but I
can't really explain what that purpose is.

Whenever you use this _asstMachinery_ Item, it will increase (buying) or
decrease (selling) the selected Asset Account balance by the amount of the
document line item. Let's see why this might NOT be what you want to do, or
rather, how to correct the error that results.

1. We buy a new custom made Conveyor System for handling pallets from
Millcreek Machine for a total of $1,895.00. We create a Vendor Bill using the
asstMachinery Item.

This Increases the balance of GL Account _1500 Furniture & Equipment_ by
$1,895, which is what we want. The balance of this account should show the

_Chapter 7: Items_ **218** CA _User Manual_


Current Value of the Furniture & Equipment we have on hand.

2. We discover that the conveyor system doesn't do what we require. Now
what, it was custom made to our specs and Millcreek won't take it back.
3. We find out that Martin's Heating & Cooling is needing a conveyor system
like this. Martin's agrees to buy the conveyor for $1,600.00 and we're happy to
be loosing $295 instead of $1,895.
4. We bill Martin's for the conveyor, using the same _asstMachinery_ Item.
5. All over and done with? No way!
Remember that the GL Account _1500 Furniture & Equipment_ is supposed to
show the **Current Value** of the equipment we own. When we check the Register
of that account (Banking Zone, Register) we discover that its balance decreased
by $1600. Have you figured out the problem yet? There's still $295 (our loss)
showing in that account. Here is a portion of the GL Detail By Account Report
showing that balance. It should be $0.00! Or rather, it should have been
decreased by $1895, not by $1600.

**Up until this point, the entire Conveyor System transactions has had no
affect on our P&L Report, only on the Balance Sheet.**

To make a correction for this we will need to write off the $295, so it will show
as a loss on you P&L, by moving the $295.00 from the 1500 account to an
Expense Account. There is no default GL Account for this purpose, the closest we
can come is _6300 Depreciation Expense_. You may possibly want to talk to your
Accountant if a situation like this occurs, possibly a separate GL Expense Account
should be set up to use for this.

It is not possible to use a Transfer to move money to an Expense account, so
we'll need to use a **Journal Entry** (select Journal Entry under the General
Ledger menu). Shown here is a transaction that will make the necessary
correction.

See Debits & Credits on page 88 if you want to figure out how we determined
which GL Account gets which column.

After this Journal Entry, all the account balances are correct again, the _1500
Furniture & Equipment_ account balance is 0.00. WThe most direct way to create

_Chapter 7: Items_ **219** CA _User Manual_


Debit and credit entries is to create Journal Entries (page 116). ell, in our test
database it is, in real life we hope you have more then one piece of equipment
that is represented in this account.

**7.13.2 Depreciation of Assets**
If you use Asset GL Accounts to track the value of your assets, you will need to
make periodic **Depreciation** adjustments to your asset accounts. Your
accountant can supply you with the corrections to make. Generally you can
legally write off Depreciation as an Expense on your Income Tax Return, but only
if your Tax Preparer filled out the proper paperwork to do so. The Depreciation
Adjustment would be a Journal Entry, like the write-off we just demonstrated.

In my own small business (sole proprietor, sole employee) I track the value of
my equipment, etc. myself, it is not legally expense-able, so I make yearly
adjustments using the Owner's Equity account instead of an Expense account. It
will not show up on the P&L that way, but still keep my **Balance Sheet** accurate.
My goal is to keep the Balance Sheet showing what the value of my business
should be if I were to liquidate it.

**7.13.3 Taxes Tab**
For this Item example, all the taxes are checked to be exempt which is the
normal for Asset Items. This is not set in stone, there are situations where you
might dispose (sell) equipment in a manner that Sales Tax is charged, but it is not
too likely. You can always change the tax status on the Invoice when you make
the sale.

```
The Other Tab is covered in the Retail Inventory Item (page 197 ).
```
_Chapter 7: Items_ **220** CA _User Manual_


### 7.14 Item Quick Edit.............................................................................................

This opens a form that allow rapid editing of Items. This form is accessed via
Item Quick Edit option of the Items Menu (pg 130 ).

**WARNING** : Please use this feature with caution, Changes can be made rapidly.

When the form opens, it does not show any Items. You will need to enter the
desired search criteria at the top, then click the **Search** button to load a parts
list. Shown here, we have loaded all of the **Inventory Items** (see Inventory Item,
pg 191 ) from the _Material_ Inventory Groups (pg. 130 ). **Item Type** is the only
required search parameter, you can only load one Item Type at a time. To narrow
the list to only the 3/8" hardware, we can type _3/8_ in the **Item Number** field and
click the **Search** button again.

After a parts list is loaded, you can go through and edit any of the fields in the
Table Control, or Data Table (page 34 ) containing the Items. The **Tax Exempt**
column has 3 options, _yes_ , _no_ , and _--_. The -- option indicates unchanged. The **UC**
check-box is Update Cost from Purchases (pg. 190 ).

**Warning** : If you make changes and/or Click the **Go Back** button, all changes
made will be saved without warning or asking. This is a very powerful tool, but
easy to misuse. Each row (Item) will be saved as soon as you click on another
row. If there are modifications in the currently selected row when you click
**Search** or **Go Back** it should ask if you want to save your changes – this pertains
to the currently selected row only, all others will already have been saved.

_Chapter 7: Items_ **221** CA _User Manual_


### 7.15 Item Bulk Edit...............................................................................................

This feature is even more dangerous then Item Quick Edit, because it changes
a lot of records at once. It is a very powerful tool, however, and can be of great
benefit if properly used.

**WARNING** : Please use this feature with caution, Changes can be made rapidly.

The Bulk Edit form was seriously revised in version 2023.1. Item Bulk Edit is
accessed via the Item Bulk Edit option in Items Menu (pg 130 ). Overall, the
revised updater should be much faster on large item lists than the previous
version was.

**Note:** When you click an Update button it will show a list of all the items that
will be affected, and will allow you to update all, cancel the update, or select
which items will be updated.

The **Filter Criteria** at top is similar to the Quick Edit, it limits which items will
be affected by the update. You can filter for text matching the Item Number, Item
Name, Sales Description or Vendor Part Number. There are multi-selection drop-
down lists for filtering by Inventory Group, Item Type, Markup Formula or
Preferred Vendor.

The various update options are broken into sections. Each section is color-
coded and has it's own titled border. Each section also has it's own Update

_Chapter 7: Items_ **222** CA _User Manual_


button.

When you click an update button it will update only the options that are check-
marked within that colored section.

Most of the update options are pretty self-explanatory, so we won't go into a
lot of detail here.

**Here is a brief rundown of the different sections of Item Bulk Edit.**

1. General Fields
    ◦ This section has updates that apply to all or most item types.
2. Inventory Settings
    ◦ Updates that apply to Inventory Items only, such as Asset account and
       Alert Level, etc.
3. Cost and Base Price
    ◦ This section has it's own Filter section, used in addition to the Filter
       Criteria at top, to further narrow down exactly which items will be
       updated.
    ◦ The updates available are for modifying the Markup Formula and Round
       To that applies to the Base Price.
4. Item Price Level Formula and Round To
    ◦ This is like Cost and Base Price update, except it applies to the Price
       Levels of the Item (pg 179 ) instead of the Base Price.
    ◦ This section also has it's own extra filter criteria.
5. Item Units
    ◦ Update options for Adding, Deleting and Editing items. Be very careful
       what you do with this!
6. Taxable Status
    ◦ Bulk Update for item's Taxable / Exempt status

_Chapter 7: Items_ **223** CA _User Manual_


When we click the **Apply** button, we get an Item Selection dialog that allows
us to accept or cancel the proposed update. The**?** column (check-box) allows
selectively excluding (by un-checking) any items you don't want to update.

There are buttons at the bottom left for checking / un-checking all items or
selected rows. If you click **Use Checked** then a Progress Dialog will show, to
indicate CA is working, and when complete another dialog will show with a
success or error message (if something failed to update). If there are errors you
should probably check the applog using the Show Log menu option (pg 151 ) and
check it for a list of the items that failed to update.

_Chapter 7: Items_ **224** CA _User Manual_


## Chapter 8: Manufacturing.......................................................................

**This pertains only to Manufactured Inventory Item s. (page 202 ) If you
don't have any of these in CA, then skip this chapter.**

When you make 'widgets' in your shop, you **Manufacture** them. If you've
been following through on the Inventory Items you will probably realize that
Classic Accounting won't magically know how many 'widgets' you have on hand.

Anything that you order from a Vendor will adjust the Qty on Hand when you
enter the Vendor Bill or do an Item Receipt. But how about the Items that are
made in-shop?

```
If you open the Item Manager zone (pg 170 ) you will see the
```
**Manufacturing** button at lower left. Click on it to open a form that allows you to
'Manufacture' the Items within CA.

On a daily basis, or on some other predetermined schedule, someone will need
to enter the shop's production of widgets into CA.

```
Here is a screen-shot of 5 Orange Widgets being Manufactured.
```
_Chapter 8: Manufacturing_ **225** CA _User Manual_


```
8.1.1Manufacture Details
This section has the “header” information of the Manufacture Document.
```
**Date**
It will adjust the Inventory On Hand as of the this Date. Try to stick with
using today or yesterday's date when possible.

**Ref #**
Will fill and increment automatically, a reference number used to find /
reference previous Mfg. documents. This works same as other document number
fields, you can enter your own number prior to saving or printing the document to
set the starting number desired.

**Memo**
Enter a general description of what is being done, and if it is a custom job you
may want to enter a PO # or something.

**8.1.2Items To Build**
Click on the blue + button to add a line to the **Items to Build** section. In here
enter the Item Number of the Item you want to build, the Unit and the Qty.

You can add multiple
Items in the list to be build
at once.

When you Save the
Manufacture it will check
that there are sufficient
components on hand to build
everything, if not then it will
display an alert message.

**Show Only Items With Components**
When this box is checked then only items that have Components entered (see
Components Tab, pg. 204 ) will be available in the Item Combo Box (pg. 34 ) in the
Items To Build section. If for some reason you need to add an Item that does not
have any Components attached.

**Add Sub-Components
This feature is known to be buggy and is not recommended**
If you add an Item To Build that has additional Component Items (see
Component Inventory Item, pg. 198 ) that need to be build, you can select the
main Item then click here to add all the required Sub-Components to this same
Manufacture document.

If the same Sub-Component is listed as a Component for multiple Items, it will
add it only once and add to the Qty for each additional time it is needed.

_Chapter 8: Manufacturing_ **226** CA _User Manual_


**Special Note:** When you generate sub-components, it will generate the
quantities of all the sub-components for the quantity of the Main Item that was
selected, but if you change the Qty of the Main Item it will not update the Qty of
the Sub-Items.

**8.1.3Item Components Needed**
You can add, remove and edit components as needed for this Manufacture. If
you have multiple Items To Build it will only show the components of the Item To
Build that is currently selected.

The Description field is editable, and is what will print on the printouts (not on
the original print). Note: this Description is obtained from the Components list,
not from the Item's Sales Description.

NOTE: Mfg uses the Average Cost of Items instead of Cost, in order to keep
Asset values more accurate.

**8.1.4Build (button)**
This is the Save button, click here to save the Manufacture. It will adjust the
Inventory on Hand Quantities for all Items that are being Manufactured (+) or
being used in the Manufacture (-).

**8.1.5Print (button)**
Perhaps you will
want to run the
Manufacture **before**
you actually make the
Items in the shop, to
see if you have
enough material on
hand. This would
provide the added
benefit of providing a
pick-list to use, as the
Print button prints a
**Manufacture Detail
Report**. This report
is somewhat crude
and provides
incomplete /
redundant
information, it could
possibly be tweaked by your Classic Dealer on request. This picture shows only
the first part of the printout, this one is over a page long.

There are several reports available on this Print button. (See Print Button on
page 40 how to access the secondary reports.) The original report was also
retained, in case you prefer it.

_Chapter 8: Manufacturing_ **227** CA _User Manual_


```
Mfg Pick List
```
This report provides a pick-list that can be used to gather all the required
components. If you print this same report via the Inventory Reports (pg. 366 ) tab
of the Report Zone you have the option of sorting by either Item Number or
Location, and the option to suppress the Labor Items.

_Chapter 8: Manufacturing_ **228** CA _User Manual_


**Mfg Detail Per Item**
This is very similar to the **Mfg Pick List** , but if multiple Items To Build are
entered it provides a break-down of each Item, rather then a combined list.
Again, it has additional parameters if printed via. the Inventory Reports.

**8.1.6Duplicate (button)**
Creates a new Manufacture document as an exact copy of the one that is
currently displayed.

**8.1.7Delete (button)**
Clicking this will Delete a Manufacture after it has been build. It will revert
(undo) the Inventory Quantity adjustments. During testing I experienced some
rough spots using this form. If the form quits working you will need to close and
reopen CA (get a fresh GUI). If you need to modify something and it doesn't allow
you to, perhaps you can Delete the Manufacture and start over.

**8.1.8Open (button)**
The usual - Opens a data table dialog allowing you to open / edit a previous
Manufacture.

_Chapter 8: Manufacturing_ **229** CA _User Manual_


**Manufacturing as a whole:**

All in all - pretty basic. Well, not really if you consider the whole process up to
this point.

```
Create GL Account setup.
Create Items - Materials, Components & Manufactured.
Purchase necessary Materials.
Manufacture Items.
```
Manufacturing - Simple? Yes. No. You be the judge.

**Warning** : A user of **Manufacture** claims his Inventory is not accurate, it was
correct then with no (thus far) explainable reason it is not. There may possibly be
bugs in **Manufacture? Note** : It has been found that altering existing Units of an
Item after it is in use can throw Inventory Count off track.

_Chapter 8: Manufacturing_ **230** CA _User Manual_


## Chapter 9: Expense Zone.........................................................................

This is where you make entries (create documents) for your outgoing money
(Purchases).

A Note on Items

Within the Expense Zone, each time you use an item (as a line item of a
**document** ) it will affect the GL Account that is set as that Item's _Expense
Account_. Some documents (Vendor Bill) allow you to enter document lines
directly to a GL Account instead of using an Item. This can be useful, but if you
use GL Accounts you won't have that purchase listed on the Purchase Analysis
report.

```
See Search Dialogs on page 52 for help on the View/Edit buttons.
```
_Chapter 9: Expense Zone_ **231** CA _User Manual_


### 9.1 Vendors............................................................................................................

You must enter a Vendor for each person or business that you buy anything
from. If you know what Terms (page 111 ) your vendor gives you be sure to fill
them in.

```
Click on the New Vendor button to add a new Vendor to your system.
```
```
The Add / Edit Vendors form has 3 Tabs besides the fields at top, which are:
```
**Vendor Name**
The **Name** is required, it is actually the ONLY field that is required in this
form! This is what prints on Documents, what the Vendor sees on the printouts
you give him.

**Name Extension**
The **Name Extension** is an internal reference field, it appears in the Vendor
drop-down lists (Name Combo Boxes) but it does NOT appear on any printed
documents. The most common use of this field is to differentiate, internally,
between various names that are same or similar. You might do business with
several branches of the same company, use this field to create a visual reference
to which branch this is, example _Acme Material Jobbers (Minerva)_ where the
name is _Acme Material Jobbers_ and _(Minerva)_ is in the Name Ext field. The

_Chapter 9: Expense Zone_ **232** CA _User Manual_


authoer find it useful to always enclose the Name Extension in parentheses () so it
is easy see that it is not part of the Name that will print.

CA will not allow saving 2 Vendors or 2 Customers with identical names.
However, the "Name" consists of Name + Name Extension, so you could still have
multiple Vendors named _Acme Material Jobbers_ as long as each one has a
different Name Extension.

**Default Purchase Account**
Here you can select any COGS or Expense GL Account. If you write a lot of
checks to this Vendor and use GL Account line entries that are usually to the same
GL Account, you can select that GL Account here and it will fill into the first line
of the Check by default.

**Balance**
This read-only field shows the current balance for this Vendor, the amount of
money you owe to this Vendor.

**9.1.2New Bill (button)**
The button at bottom left allows you to create a new document for this Vendor.
To create a document other then a Vendor Bill this button's pop-up list contains all
the available documents. See Drop-Down Buttons on page 38 for more info. This
button was added in v2020.1.

**9.1.3Create Customer**
There's a **Create Customer** option in the New Bill button's list that will open
the Customer form with the name and address, etc filled out same as the current
Vendor. Used to quickly add this person / company to your Customer list.

**9.1.4Vendor Info Tab**
Most of the fields are self-explanatory. None of them are required in order to
use this Vendor. We will detail only a few of them.

**Print On Check As**
If you print Checks with CA then this is what will print in the **Pay To** line of
the Check. See Printing Checks, pg. 324.

**Address
Warning** : If the address has only one Address Line instead of 2 as shown
here, then use the 1st line and leave the 2nd line blank. Otherwise the Name /
Address may not print out properly on documents.

CA has a build-in list of USA City / State / Zip Codes, when you type in the **Zip
Code** , then the City and State will auto-fill for you. When tabbing through the
fields you should just tab through the City and State fields, it is not necessary to
manually enter this text as they will Auto-Fill.

_Chapter 9: Expense Zone_ **233** CA _User Manual_


In v2020.1 a Disable Country Fill setting (pg 116 ) was added to Global
Settings tab of Company Options that disables auto-filing the Country field (but
still auto-fills City and State).

There is also a setting in the Global Settings of Company Options (pg 116 ) that
controls whether the City name is converted to all uppercase or not.

**Special Note** : There are situations where it is desirable to use numbers for
identifying customers or vendors (an Auction, for example). An alternative setup
for name / address is as to place the Vendor's **ID Number** in the **Name** field and
the Vendor's Name in both the **Name Extension** and the first address line. Then
it will print on documents like this:

_3456
Charles McHenry
987 S. Main Street
Winesburg, OH 44828_
and display in the Name Combo Box like this: _3456 Charles McHenry_

**9.1.5Additional Info Tab**
This tab provides some settings that are used by CA. Try to fill in as much as
possible here.

**Type**
This is a preset list of different 'Types' of Vendors. This setting has no affect
anywhere and is only visible here.

This list can't be edited. To really be of practical use this should be a user-
defined list and should be usable to filter the Vendor List and certain Reports. As
it is currently it has little practical value, but that could possibly change in the
future.

**Terms**
This field determines the default Terms (pg 111 ) for this vendor. When you
create a new **Bill** for this Vendor, the Terms that are selected here will
automatically be filled in the document's Terms field. If needed, the Terms can be
changed on the document, it is not limited to using only this Terms. Terms are
used to determine the Due Date, Discount Percentage and Discount Date of a
document.

**Credit Limit**
Here you can enter the Credit Limit that you have with this Company.
This feature was "activated" in version 2020.1. If this number is greater then
zero it will now display a warning if you save a document that will potentially put
you over the Credit Limit set.

This works similar to Credit Limit for Customers (pg 267 ), but has more
complex logic to calculate orders placed and Item Receipts.

_Chapter 9: Expense Zone_ **234** CA _User Manual_


**Account No.**
This is for
entering the Account
Number that you
have with this
company. This
number appears on
the Purchase Order
printout.

**Tax ID**
If you need to
provide a 1099 or
other tax form to a
Vendor then you will
also need to know
that Vendor's **EIN** or
**SSN** on file. This
field provides a
convenient storage
place for that number.

**Eligible for 1099**
Check this box if you may possibly need to file a 1099 form for this Vendor. In
the Reports Zone there is a 1099 Report (pg. 364 ) that will show how much
money you've paid, in a specified time frame, to each of the Vendors that has this
box checked.

```
Tax Time just got easier! That why you're doing this, isn't it?
```
**Is Cash Vendor**
If checked, then you can Edit the “Pay To The Order Of” text on a check when
writing the check. See Checking, page 321.

**Notes**
A general field for entering notes on this Vendor. Internal reference only, does
not appear on any printouts and can't be seen anywhere else but here.

**Alert Notes**
Any text you enter
here will pop up in a
message box like
shown here each time
you select this Vendor
to create a document.
It shouldn't be hard to figure out that this can be a very valuable feature.

_Chapter 9: Expense Zone_ **235** CA _User Manual_


```
Groups
See Org Groups on page 342
```
**9.1.6Document History Tab**
This allows you to view any and all documents that you have created for this
Vendor. This is often the easiest way to find some old Bill or PO.

**Sorting** : Click on any of the Column Headers of the Data Table to sort the list
by that field. Click again to reverse (A-Z / Z-A) the Sort Order. This table was
revised to load faster and implements Table Row Sorting (pg. 36 ).

**Document Type**
Selecting a specific document type in this list, like **Vendor Bill** , will limit the
list to show only that type of document. This makes it easier to find something
after there are many documents in the list.

```
Note that this list will only contain document types that exist for this Vendor.
```
**Doc Status**
This is a **Filter** that limits the list to show only Documents that are OPEN, or
only the ones that are FULFILLED, etc.

**Open Document**
This Button will open the document for the selected line in the Data Table. If
the Document's Status is OPEN then you can edit or otherwise work with it from
here.

Double-clicking on a row will open the document for viewing / editing. Doing
a Ctrl+click on a row will open the document's print preview screen.

When you close that document, the view will return back to this screen. What
happens is several forms are open at once, but you can only see and work with

_Chapter 9: Expense Zone_ **236** CA _User Manual_


the one that was last opened, the one on top of the stack. When you close a form,
you can see the one immediately underneath it again. See Go Back / Close on
page 42 for a bug note on this.

See Deleting / Merging Customers on page 271 for info on merging duplicate
Vendors.

_Chapter 9: Expense Zone_ **237** CA _User Manual_


### 9.2 Quote Request.................................................................................................

A Quote Request is a document for requesting price quotes from one or more
Vendor. This document is the "first in line" for Expense documents. A QR can be
converted into a Purchase Order, Item Receipt or Vendor Bill.

There are a few points of this document that are different from other
documents, which we will cover here. Otherwise it is used like other documents.

**9.2.1Multiple Vendors**
All other documents have one Vendor (or Customer) per document. On a QR
you can have multiple Vendors.

The List Box that normally contains the entire list of Vendors is empty, instead
you Add and Remove Vendors to the Quote Request using the and

```
buttons. The Vendor list will remember all the Vendors you placed it
```
in, but when printed it will print with the currently selected Vendor, and will also
remember the current Vendor when you save the document.

You can add internal notes (for yourself) for each different Vendor by Double-
clicking on the **Vendor Note** label that is to the left of the Repeat Frequency and

_Chapter 9: Expense Zone_ **238** CA _User Manual_


Ship Via fields. If a note is attached this label will become green. Double-click on
the label again to open the Note.

**9.2.2Status**
Unlike other documents, which the status automatically changes when the
document is fulfilled, QR has a customizable list of status, and must be manually
changed. Update this list via QR Status (pg 114 ) in Company Options dialog.

To consider a document as Closed you must check-mark the **Closed** check-box
that is in the center of the screen (between the bill to and ship to addresses).

**9.2.3Repeat Frequency**
This feature is for the purpose of allowing the QR document to act as a
"Template" to be used for Purchase Orders or Vendor Bills that re-occur on a
regular basis.

This feature does not come with any bells or whistles yet, but if you have a
Repeat Frequency set other than **ONE TIME** then after you exported the QR once
it will display a label with the date of the next occurrence.

On the Expense And Payable tab (pg 363 ) of Reports Zone there is a report
**Repeating Quote Requests** that allows you to see what expenses are coming up
based on the Repeat Frequency and the date of the last document exported. This
can be useful for keeping you reminded of monthly utilities, quarterly taxes, etc

_Chapter 9: Expense Zone_ **239** CA _User Manual_


### 9.3 Purchase Order...............................................................................................

If you order supplies or materials from one of your Vendors, you can create a
Purchase Order for it.

Once you receive the Bill for that order, you can convert the PO into a Vendor
Bill in one of two ways:

1. Create a new Vendor Bill for that Vendor. A pop-up will appear that allows
    you to choose from open PO's to import.
2. Open the PO and use the 'Create Bill' button in upper right corner.
    When you create a PO its status is _OPEN_. Once all the lines / quantities have
been Billed, then the PO's status will become _FULFILLED_ (closed)_._

The **Status** combo-box below the **Create Bill** button allows manually closing a
Purchase Order by setting the Status to FULFILLED.

```
9.3.1PO Information
In the left Combo Box select the Vendor whom you are placing this order with.
```
_Chapter 9: Expense Zone_ **240** CA _User Manual_


The right Combo Box is for selecting the place that this order is supposed to
**Ship To**. This automatically fills in the Company name / address for you, but you
can select any Customer from the list. If the selected name has multiple Ship To
addresses you can choose the desired one using the drop-down list above the Ship
To address block.

To the right of the Ship To (Customer) box is a Search button, this opens the
**Search Customers** dialog so you can search for a Customer to the Ship To box.

**Create Bill Button**
Once you receive the order, you can re-open the PO and click this button to
create a Vendor Bill (page 250 ) for it. It will open the **Select Items to Import**
dialog. There is a line for each of the Document's Line Items. By default they are
all checked, and the **Imp Qty** is same as the **Qty**.

Note: You can create several Bills from the same PO if the Vendor splits it into
multiple shipments / Bills. You can also import from multiple PO's into one Bill,
see Vendor Bill.

If you are receiving only part of the order you can un-check any line to not
include it on this bill, or you can adjust the **Quantity** to import only the quantity
that was received. The **Qty Imp'd** column shows how many of this line were
previously Imported to a Bill or Item Receipt.

The **Item** column displays the Item Number (page 187 ) and its QOH that is set
in the Item itself, the **Doc Item #** column shows the Vendor Part Number, or
custom-entered Item Number that is displayed on the Purchase Order.

This button has a **Drop-Down** that allows you to create an Item Receipt
instead of a Vendor Bill. In the displayed example we are Importing to an Item
Receipt (page 246 ).

**Status**
If you have a PO that you want to close (FULFILL) and not all of the line items
have been received or Billed, then you can manually change the status to
FULFILLED to remove it from your list of open Purchase Orders. If you close a
PO, the Item Qty On PO numbers will update and not include the Items on
FULFILLED Purchase Orders, even if the Imported Qty is less then the Qty.

**Date**
Enter the Date you are placing this order. This field is required, you can't save
the document without a date.

**PO Number**
This will auto-fill with the next sequential number when the PO is saved. You
may want to enter the correct (starting) number on the first PO that you create.
This number can be changed if needed.

_Chapter 9: Expense Zone_ **241** CA _User Manual_


**Vendor**
The text field auto-fills with the selected Vendor's name and address. It can be
edited if needed. If you edit this, your changes are only saved with this
document, it will not change the Vendor's address or anything.

**Ship To**
If you selected to **Ship To** a Customer that has multiple Ship To addresses,
then you can select which one to use in the Combo Box above the Ship To address
field. The text in the Ship To field can be edited if needed, same as the Vendor
field.

**Ship Via**
Select the method you would prefer to have this order shipped, if applicable.
To edit this list, see Via Methods on page 113.

```
Expected
The Date that you expect or need the order to be at your shop (optional).
```
**F.O.B.**
( **Freight or Free?) On Board** is a location, such as a city or building, where
the merchandise is located, or that the seller of the product will furnish the
transportation to. After that point, the buyer assumes responsibility for
transportation costs and / or arrangements. For the sample PO shown, the F.O.B.
might be _North Easton, MA_ , which would be saying that the merchandise is
located in North Easton, MA, and you, the buyer, will furnish (pay) transportation
from their location to your location. If this company ( _Acme Widgets, Inc._ ) had a
warehouse in Pittsburgh PA, the F.O.B. might be _Pittsburgh, PA_ which means that
they will ship (or stock) the item to the Pittsburgh warehouse at no cost to you,
then you would pay or provide the transportation from Pittsburgh to your shop.
Or maybe they make regular shipments to a location near you, and they're willing
to send your order along at no charge if you pick it up at that place, then it might
be something like F.O.B. _Hershberger Hardware, Baltic, OH_.

There is no F.O.B. field in for Invoices in CA, but the same would apply to
Invoices as well, then YOU are the seller, providing the transportation to the given
F.O.B. point and your Customer paying or providing the rest.

**9.3.2Document Line Items**
This Table Control is where you enter the 'Line Items' of the document. See
Table Control on page 34 for general help.

```
Let's take a look at each field (column).
```
**Item**
Type in the first characters of the Item Number that you want to order. This
must be an Item that exists in CA. See Item Combo Box on page 34 for help. This
does NOT print.

_Chapter 9: Expense Zone_ **242** CA _User Manual_


**Item #**
This displays the Vendor's Part Number (pg. 189 ) if you entered one, or your
Part Number if you did not. This is the Item # that appears on the PO printout.

This field can be edited. You might create one Item in CA to represent a lot of
different real-life parts. For example, I have an item _WPCRYPKH_ ( **W** atch **P** art,
**Cry** stal, **PKH** style) to represent one style of watch crystal (lens). This particular
style comes in 40 + sizes, so when I add one to a PO I change the Item # field to
read something like _PKH 45.5_ , so my Vendor will know exactly which crystal I
want.

**Description**
This is the main description that prints on the PO. It fills in with the Item's
Purchase Description (pg. 188 ), and can be edited as desired. This field
implements the Multi-Line Text Editor (see page 35 ).

**Unit**
If an Item has multiple Units then this is often wrong by default, so always
double-check and correct as needed. It wants to fill in the **Def Selling** unit and
often you want the **Main** unit instead. See Units Tab on page 195 for more info.

**Measure Quantity**
This column is an extra multiplier that can be used as a linear measurement by
entering the piece length. This will then be multiplied against the quantity to get
a total price. See the Invoice's Meas. Qty. (page 280 ) for further details. This
column is not visible by default, see Column Width / Position / Visibility on page
35.

**Qty**
Enter how many of this Item you want. Keep the **Unit** in mind, don't order 24
cases when you only need 1 case of 24 pieces!

Since v2020.1 when an Inventory Item is selected the Qty will auto-fill with the
Order Min Qty (pg 196 ) if it is more than 1.

**Rate**
This is the Per Unit Price. If you have Cost entered in the Item it will auto-fill
based on the Unit selected, but it can be changed if needed.

```
Line Total
This is a calculated field (read-only), it multiplies the Rate times the Qty.
```
**Notes (Line Item)**
This is for internal reference only, here you can attach a note to let other
employees know what this Item was ordered for, or something similar. Maybe a
ref number such as your customer's PO #

_Chapter 9: Expense Zone_ **243** CA _User Manual_


You can't write directly in this
field. Instead, click on it, or hit the
Enter key when the focus is on this
field, to display a pop-up that allows
you to enter and edit the note. Click
the **X** block in upper right corner of
frame to close the pop-up, OR hit
either the **Tab** key or **Ctrl+Enter**
key combo on your keyboard.

**Job**
This allows you to select an open Customer Job (Jobs Tab, pg 270 ) or Company
Projects (pg 116 ) that this line applies to.

**R'd**
This displays the total Quantity of this line that has already been received,
either placed on an Item Receipt or a Vendor Bill.

**Help Text (Tool Tip)**
When you hover your mouse over a line on the document form a "Tool Tip
Text" box appears that displays information on this row. In v2020.1 this "tool Tip
Text" was updated to include the Min and Max Order Qty info.

**Along the bottom of the Purchase Order form are a few additional
fields:**

**Notes (Document)**
This prints on the PO as a note to your Vendor. Use it to communicate any
special instructions.

**Memo**
This is for internal reference only, does not appear on printout. It does appear
in the **Find Document** dialog, use it for an easy-to-find reference point for
entering some note to let other people (or yourself) know some basic detail of this
document.

Usage suggestion: Some companies start PO's long before they order, yet
want the PO date to show when the PO was started, or how long its been Open.
In this scenario the Memo can be used to store the actual Order Date. (VPWR)

```
Total
This is a calculated field showing the total sum of all the lines.
```
_Chapter 9: Expense Zone_ **244** CA _User Manual_


**9.3.3Sample of PO printout**
Here is a sample of the Purchase Order printout. Note that the Item Number
displayed here is the Vendor's Item Number, not our number _wgtRed_.

_Chapter 9: Expense Zone_ **245** CA _User Manual_


### 9.4 Item Receipt....................................................................................................

**An Item Receipt is used only if you are tracking inventory and using
Inventory Items.**

It is used for placing Inventory Items 'in stock' before the bill is received. Say
you ordered a pallet of Red Widgets on Tuesday and receive them on Thursday,
and you know you won't get the Bill until about 2 weeks later, at the end of the
month, but you need CA to show the Items in stock so you can use them in
Manufacturing (page 225 ) or to sell to a Customer.

This form works pretty much same as the Purchase Order form (page 240 )
except it doesn't have as many options.

**Note on shared form:**

The Item Receipt, Vendor Bill and Vendor Credit all share the same form for
displaying documents.

The document type is prominently displayed near top, along left side. This
text is a different color for each different document type, to make it easier to
visually tell them apart.

When you create a new Item Receipt and select a Vendor that has open
Purchase Orders, then the Select Items To Import dialog (pg 79 ) shown here will
pop up, displaying all the open PO's for that Vendor. You can select any Items
from any of the available POs to add to your Item Receipt.

_Chapter 9: Expense Zone_ **246** CA _User Manual_


You can also use an **Item Receipt** to receive Items even if you didn't make a
PO for the order. Just enter the line items like any other document.

```
Here is a view of the Item Receipt created from the above import dialog.
```
**Ref No.**
You must enter something here. Some Vendors will enclose a packing list or
other documentation that has a reference number you can enter here, otherwise
enter a note, a_?_ or whatever suites your fancy or purpose. _This is Not an auto-
incrementing number, you must enter something for each document_**.**

```
Update Item Cost
See Update Item Cost on Vendor Bill for info (pg 251 ).
```
```
P.O. Rec # (column)
This displays the PO Number of the PO that this line was imported from.
```
**9.4.2Create Bill**
From within the Item Receipt, you can create a Vendor Bill (page 250 ) for this
Item Receipt using the **Create Bill** button. It opens the 'Select Items to Import'
dialog, then generates a Vendor Bill if you click OK.

_Chapter 9: Expense Zone_ **247** CA _User Manual_


Following is a view of the Vendor Bill that was created from the previously
displayed Item Receipt. Notice that the Ref No. is different, it did not transfer the
“Rec'd 4/25” from Item Receipt, which forced entry of a Ref No.

Saving the Vendor Bill will **Delete** the Item Receipt if all of the Items have
been billed.

**Special Note:** The Item Receipt is a Temporary document. When you create a
Vendor Bill for any Items on an Item Receipt, they will be removed from the Item
Receipt, or the quantity adjusted if only some are billed. As soon as no lines exist
on the Item Receipt, it is deleted from the system. If you manually delete / adjust
lines on an Item Receipt, it will reopen the attached PO, and/or adjust your
Inventory Qty On Hand.

If you attach document(s) (see Attachments, pg 344 ) to an Item Receipt they
will automatically transfer to the Vendor Bill when the final item is transferred
and the Item Receipt deleted. (was not doing so, this bug was fixed v2024.1)

When you create a Vendor Bill from an Item Receipt that made from a
Purchase Order, then the document 'links' will switch back to the Purchase Order,
that is the **P.O./Rec #** column will show the Purchase Order it came from
originally, not the Item Receipt which doesn't exist anymore.

_Chapter 9: Expense Zone_ **248** CA _User Manual_


Here is a view of the **Item Restock List** printout that prints when you click
the **Print** button on the Vendor Bill form. This printout shows the Bin Location of
each Item (if filled in), its intended purpose is to use as as a check-list when
placing items in stock after receiving them.

If text is entered in the Line Notes field it prints on this document - the bold
text “Martin Interiors – SO #682” in this sample.

_Chapter 9: Expense Zone_ **249** CA _User Manual_


### 9.5 Vendor Bill.......................................................................................................

For everything you purchase, you should enter as a Vendor Bill (even if you
didn't create a PO for it). A **Vendor Bill** is the Invoice that your Vendor gives
you, the amount you're supposed to pay for the goods / services they provided.
This is what tracks Accounts Payable (pg 86 ).

**Important: A Vendor Bill should be entered as soon as you receive it, you
shouldn't wait until you pay it**. This is to keep your Accounts Payable accurate.

In a Vendor Bill form there are 2 tabs for document lines, you can either enter
**Line Items** , which uses **Items** , or you can use the **Account Items** tab which
uses **GL Accounts**. It is advisable to use Line Items whenever possible, because
it will give more reporting detail then Account Items. Account Items will not
show up on a report of Items Purchased.

See the section on Credit Card Example on page 95 for a usage where an
Account Items entry is appropriate.

You may want to create a number of Items specifically to use on Vendor Bills to
track your purchases. Many of these items would not be suitable for use on an
Invoice, as it's not something you would sell to your Customers. It may be helpful
to have all of the item names start with _exp_ _ or something similar to avoid using

_Chapter 9: Expense Zone_ **250** CA _User Manual_


them on Customer Invoices by accident. It also makes them easy to find, just type
_exp_ and all the expense items will appear for you to select from.

**9.5.1Update Item Cost**
In each Item there is an option for Update Cost from Purchases (pg 190 ). That
update will occur ONLY if this **Update Item Cost** option on the Vendor Bill is
**checked** when saving the Vendor Bill. If this checkbox at the top of the form is not
checked it will not update any Item Costs regardless of the setting in the Item.

When you create a new Vendor Bill (before being saved the first time) this
option is checked. If you recall an existing Vendor Bill, or after you save it the
first time, this option is not checked. You can manually check it before saving to
make it update cost.

**9.5.2Importing Items to Vendor Bill**
If you create a new Vendor Bill for a Vendor that has any OPEN Purchase
Order (pg 240 ) or Item Receipt s (pg 246 ), then the Select Items To Import dialog
(pg 79 ) will appear and allow you to add the line items from these documents onto
your Bill.

This both reduces your typing time and also sets the imported document
status to FULFILLED (tells the system that the document is closed).

This dialog allows you to check the desired document(s) to import and the
Item(s) desired to import from each Document.

**Ref. No.**
The Reference Number field is used to enter the Vendor's Invoice Number.
**This is not an auto-increment field, you must enter something on every Bill**.

```
Invoice Date
The Date on the Invoice you received.
```
**Vendor Terms**
You must select the Terms (pg 111 ) for this Bill. This determines the Due Date
and Available Discount. This field will auto-fill with the default Terms set for the
Vendor (page 234 ), if any are set.

If a Fixed Date terms is selected then the **Vendor Terms** label will become
green, and you can modify the Due Date for this particular document by double-
clicking on the green label.

```
Due Date
Read-Only field that is calculated from the selected Vendor Terms.
```
**Discount Date**
Read-Only field shows the last Date you can take a discount on this document,
based on the Vendor Terms selected. Blank if there is no applicable discount.

_Chapter 9: Expense Zone_ **251** CA _User Manual_


**9.5.3Line Items**
Entry of Line Items is same as in Document Line Items for Purchase Orders,
see page 242 except for a few additional columns.

**P.O./Rec. #**
If this line was Imported from a PO or Item Receipt, then this field will display
the Ref. No. of that document.

**Markup %**
This is a calculated field that shows the Markup percent of the Cost (the Rate
on this line item) and the Base Price (pg. 178 ) of the current line's Item. The
calculation formula is: 1 minus (Cost divided by Base Price). This number can be
manually editable, which will update the displayed Base Price. This field will
recalculate if you modify the Rate (cost) of the Item. If the Item's cost has
changed, this will allow you to see if the change is enough to require modifying
the Item's Cost to reflect the Vendor's price increase. Note: If the Update Cost
from Purchases (pg. 190 ) option is checked then the cost will automatically
update.

**Base Price**
This shows the current line Item's Base
Price (pg. 178 ) and is used in conjunction
with the Base Price column to show your
current markup on this Item. If the Item
has no Markup Formula (pg. 178 ) set, then
this field is editable and allows you to
change either the Base Price directly or the
Markup %, which will recalculate the Base Price. If any changes are made that
affect this Base Price number, then you will get a pop-up when you save the Bill
that allows updating the Item to show these changes. Note: If the Update Cost
from Purchases (pg. 190 ) option is checked then the cost will automatically
update, and if there is a Markup Formula entered the Item can't be updated from
here.

_Chapter 9: Expense Zone_ **252** CA _User Manual_


**9.5.4Account Items**
Here we're showing an entry for a Credit Card statement. See Credit Card
Example on page 95 for details.

The Credit Card account was used to pay Vendor Bills (see Paying with Credit
Card on page 260 ). The entry Amount of this statement is the total New
Purchases on our Credit Card Statement. See Credit Cards on page 381 for more
details.

The first line of Account Items will auto-fill with the selected Vendor's Default
Purchase Account (pg 233 ), same as the Check form does.

```
9.5.5Line Links (button)
See Line Links (pg 38 ) for details.
```
```
9.5.6Payments (button)
This button does 2 different things.
```
_Chapter 9: Expense Zone_ **253** CA _User Manual_


**Create Payment**
If the Vendor Bill has no payments attached, then clicking the Payments button
will open a dialog that allows you to enter information to create a payment for
this Vendor Bill.

The intent for this feature is primarily to enter payments made with Credit
Cards, where the payment is already processed when you enter the Vendor Bill.

```
When using this feature:
```
- You can choose the Payment
    (bank / credit card) Account.
    ◦ You can set the Default Payment
       Account for Pay from Vendor Bill
       to use in Expense Settings
       dialog (pg 146 ).
- You can choose the Payment Date.
- If the Assign Check Number from
    Pay Bills setting (pg 146 ) is
    checked then you can enter a
    check # here, but only on Bank accounts, field is disabled for Credit Cards.
- You cannot create a partial payment.
- You cannot combine multiple Vendor Bills on one Bill Pay Check (payment).

**View Payments**
If you click the **Payments**
button when the displayed Vendor
Bill already has one or more
payments attached it will show a
dialog that displays the payments
made, and allows opening a
payment (Bill Pay Check) from the
dialog. This is about same as the
Payments button on Invoice
screen.

**9.5.7Deleting Vendor Bill**
If you delete a Vendor Bill that is linked to
one or more Purchase Order, a pop-up message
will appear asking if want to Re-Open the
Purchase Order(s) if it is already Fulfilled.

_Chapter 9: Expense Zone_ **254** CA _User Manual_


### 9.6 Vendor Credit..................................................................................................

A Vendor Credit document represents a Credit Memo (pg 287 ) that you
received from your Vendor for merchandise that you returned or otherwise
received credit for.

Creating and using a Vendor Credit is similar to a Vendor Bill. See Receiving a
Vendor Credit Refund on page 390.

_Chapter 9: Expense Zone_ **255** CA _User Manual_


### 9.7 Pay Bills...........................................................................................................

After a Vendor Bill has been entered in CA, you need to pay that bill. The Pay
Bills button opens a form for paying Bills. Once a Vendor Bill has been created, it
will be listed in here.

**Warning** : By default, it only displays the Bills that have a Due Date on or
prior to Today. You need to toggle the date filter setting at lower left to get it to
show all bills. This date filter can be a useful feature, but you need to remember
that it is there. It's easy to overlook Bills that should be paid if you forget to
check the due date.

If you want to create payments only for bills due now, set the **Due on or
before** Date to no earlier then the next day that you plan to pay bills, otherwise
some bills may become overdue by the next time you pay bills.

An option named **Discount on or before** was added in v2020.1. Selecting
this option shows only Vendor Bills that have a Discount available on or before the
selected date.

This form requires Pay Bills security zone clearance instead of Expense. See
Users, page 125.

Below the Due Date selector there is a status label that shows how many
Invoices are showing, and how many are selected (checked).

A **Limit To Vendor** option was added, pick a Vendor from the list in top right
to show only Bills from the selected Vendor. The Due Date filter still applies! The

_Chapter 9: Expense Zone_ **256** CA _User Manual_


Vendor list shows only Vendors that have unpaid Bills.

```
Added Bill Date and Memo columns to table.
Added Column Widget and Table Row Sorting (pg 36 ) to the table.
```
Once a Payment has been generated, a **Bill Pay Check** will appear in the
Banking Zone, under Checking (page 321 ).

**9.7.1Payment Account fields**

```
Payment Date
The Payment Date that is to appear on the Bill Pay Check you are creating.
This date automatically reset to Today when you close and reopen the form.
```
**Payment Account**
This is the Checking, Cash or Credit Card account that you are using to pay
this Bill. Always double check that it is correct before you click the Pay Bills
button!

**Bank Balance**
This Calculated field displays the current balance of the selected Payment
Account.

**9.7.2Limit To Vendor**
Select a Vendor from this list to limit the Vendor Bill list to only Bills from this
Vendor. Select the blank entry at top to show all Bills again.

```
Note: The Due Date restrictions still apply if a Vendor is selected!
```
**9.7.3Table Fields (Columns)**
This table has a Column Widget that allows customizing the column width /
order / visibility. This is a Manual Save only – you must select the **Save Current
Settings** option to actually make it save the columns. Saved settings will be
applied the first time you open this screen in a session.

**?**
Check (click) this box for each row that you want to create a payment for. Use
the **Select / Unselect All** control below the table to check / uncheck all the rows.

```
Due Date
This is the Date that the Bill is supposed to be Paid by. The Due Date is
```
_Chapter 9: Expense Zone_ **257** CA _User Manual_


calculated from the Bill's date based on the Terms selected for that Bill (see page
111 ) (read-only).

```
Vendor
The Vendor this Bill (row) is from (read-only).
```
```
Ref#
The Ref. No. of this Vendor Bill (read-only).
```
```
Memo
Shows the Vendor Bill's Memo field (read-only)
```
```
Bill Total
Shows the original total of Vendor Bill (read-only)
```
```
Owed
The total that is still owed (due) on this Bill (read-only).
```
**Disc Date**
You must make the payment by this date to be eligible for the prompt-payment
discount, if there is any (read-only). This date is calculated according to the
Terms selected on the Bill.

**Disc Amnt**
If a Prompt Payment, or any other Discount is deductible from this Bill, enter
the amount of the Discount here. This will auto-calculate based on Terms, but can
be manually changed, if needed.

**Disc GL**
This is the GL Account that is used for the Discount, if any is taken. This could
be either an **Income Account** (additional Income), a **COGS Account** (deduction
from Cost of Goods Sold) or an **Expense Account** (deduction of Expenses), but
you should have a plan for this and be consistent in the Account you use. See
Default Discount GL on page 146 for further help.

**Payment**
This is the total amount you are paying on this Bill. When you check the? box
it will fill in the Owed amount (less Discount Amount) for you. If you don't want to
pay the entire bill at this time, you can change this number to create a partial
payment.

The Total of Payment + Discount will be applied (paid) toward the Bill.
Once a Vendor Bill is Paid in Full, then the Bill's Status will change from OPEN
to PAID.

_Chapter 9: Expense Zone_ **258** CA _User Manual_


**9.7.4Other Controls**

**Select / Unselect All**
Click here to check or un-check all the boxes in the? column.
In v2020.1 this check-box got some additional functionality: Right-Clicking the
box will set the check-mark state of all selected (highlighted) rows to opposite
state of what the Select / Unselect All box is. This can help speed up the selection
process by toggling selected rows to opposite state.

**Calculate Eligible Discounts**
Click to re-calculate the discounts that are applicable.
**Warning** : The Discount Percent and Due Date might not calculate properly
after modifying an existing Terms (page 111 ). Close and reopen CA to resolve.

**Total**
This displays the Total of all the **Payment** fields of the Bills that are checked
(read-only).

```
Bill Per Check
This specifies how many Vendor Bills are placed on a single Check.
```
- If set to 0 this feature is disabled, has no effect.
- If set to 1 then it will generate a separate check for each Vendor Bill
    selected.
- To prevent the stub of your check print from overflowing set this number to
    about 11 or 12, the maximum number of Vendor Bills that will print on a
    single stub.
You can set a default value for this option in Expense Settings, see Bills Per
Check (pg 146 ).

**Pay Bills**
Click on this button to create payment(s) (Bill Pay Check) for the checked
line(s).

If Bills for more then one Vendor are selected, it will create a different Check
for each Vendor.

If more then one Bill is checked for one Vendor it will create only one Check
for that Vendor, for the total of all the Bills, unless it is set differently via the Bills
Per Check setting (see pg 146 ).

If one or more Vendor Credit documents are checked and the total Payment of
all the checked documents for that Vendor is negative then it will generate a
Receive Payment instead of a Bill Pay Check (it will show a message box to
confirm that you received a refund from this Vendor). See also Receiving a

_Chapter 9: Expense Zone_ **259** CA _User Manual_


Vendor Credit Refund on pg 390.

If the Assign Check Number from Pay Bills (pg
146 ) option is checked in Expense Settings it will
display the dialog shown here that allows assigning
the Check Number and to print the check.

- If you click **OK** to assign the check # it will tag
    the check as Printed, even if Print Check is not
    checked.
    ◦ If **Print Check** is checked it will print the check using the print settings
       from the Check form's Print button.
- Clicking **Don't Assign** will not mark check as printed, but still create it.
- **Cancel** will abort the pay bill process
    For notification of successful payment(s) created CA will briefly display a
message on the screen.

If you need to undo a Payment that was created, open and Delete the Bill Pay
Check using Checking (page 321 ).

If you need to undo a Vendor Credit Refund that was created, open and Delete
the Received Payment that the process generated. See Receiving a Vendor Credit
Refund on pg 390.

**9.7.5Paying with Credit Card**
If you used a Credit Card to pay your bill(s) select the correct Credit Card to
use in the Payment Account list and process the payment same as if you were
creating a Bill Pay Check.

Credit Cards are not printed on checks, but you may print it on plain paper for
your records if you wish.

Using a Credit Card to make payments is explained in Credit Card
Example4.4.4 on page 95 if you need more information.

_Chapter 9: Expense Zone_ **260** CA _User Manual_


## Chapter 10: Income Zone........................................................................

```
This is where you make entries for incoming money (your income).
```
Note: In the Income Zone you can't use GL Accounts directly, you must use
Items. **Items are linked to GL Accounts** , each time you use an item in the Income
Zone, it will make an entry in the GL Account that is set as that Item's _Income
Account_. If you don't understand that, stop and make a serious effort to learn how
GL Accounts and Items are related to each other, as this is the cause of a lot of
confusion among beginning users of accounting systems.

_Chapter 10: Income Zone_ **261** CA _User Manual_


### 10.1 Income Document Flow.................................................................................

```
The basic flow of documents in the Income Zone is as follows:
```
1. Enter the Customers (page 263 ) if he/she doesn't already exist in your
Customer List.
2. Quote a product or service to your Customer using an Estimate (page 274 ),
and send a copy for review / approval.
3. Convert the Estimate to a Sales Order (page 275 ) when the Customer
approves the Estimate.
4. If needed, you can generate Purchase Order (page 240 ) from either the
Estimate or the Sales Order to order the needed Items.
5. Convert the Sales Order to an Invoice (page 277 ) once the Order is
complete and ready to ship / pick up. You can start at this step, and create an
Invoice directly, without an Estimate or Sales Order, which is what most users of
CA do, most of the time.
6. Create a Receive Payment (page 289 ) for the Invoice once the Customer
pays the Invoice.
7. Payments received are used for making Deposit (page 326 ) to the bank.
You can 'start' the Invoicing process at step 2, 4 or 5, but you can't skip step 1.
You must enter the customer information before you make a sale.

You can skip from step 2 to step 5, without using step 3, if needed.
There is another form, Sales Receipt (page 294 ), that combines step 5 and 6
for using as a **Point-Of-Sale** system (using at checkout, like a cash register). You
can't use a Sales Receipt to complete an Estimate or Sales Order, and you can't
use it to create a Charge Sale, it's strictly for cash sales. If you use this form you
may possibly make most of the sales to a single 'Customer' name Cash.

There are some special features and settings for the Sales Receipt, see the
Sales Receipt tab of Income Settings dialog (pg. 139 ). Most of these features are
aimed at more flexibility and faster item entry via Barcode Scanning (pg. 297 ).

_Chapter 10: Income Zone_ **262** CA _User Manual_


### 10.2 Customers.....................................................................................................

Customers are the people and businesses you sell your products or services to.
You must enter and maintain your Customer list in CA. When entering a
Customer, take time to check all settings and make selections wherever possible.
In particular, check and set the Price Level, Terms and Credit Limit.

```
10.2.1 View / Edit Customer
See page 53 for usage of the Name Search Dialog.
```
**10.2.2 Inactive Customers**
If you have a Customer that you no longer do business with, and you don't
want that Customer to show up in your Customer list anymore, you can set the
Customer to Inactive using this dialog.

The Search Customers list shows only 'Active' customers by default, to find an
Inactive Customer, click on the **Show Inactive** check-box at the upper right.

To set a Customer as Inactive, select the customer in this list, then click on the
**Inactivate** button at bottom left. To re-activate an Inactive Customer, first show
the Customer using Show Inactive, then select the Customer and click the
**Activate** button at lower left.

**10.2.3 Customer Name**
Each Customer must have a Name. In the Name Box es (see page 29 ) that
appear throughout CA, it shows the Name followed by the Name Extension, if
there is any.

**10.2.4 Name Extension**
Names should be unique, if you have 2 Customers with the same name you
need some way to tell them apart in CA. The **Name Extension** field is used for
this purpose. This Name Extension is only seen internally, it does not appear on
printed documents, so use it at will. _Example_ : if you have 3 customers named
"John J Miller", give each one a different extension, say one is _(Grandpa)_ , another
is _(Smiths Grove, KY)_ and another is _(TR 95 Mlbg)_. Throughout the system, in the
name drop-down boxes, they will then appear as: _John J Miller (Grandpa)_ , etc.,
which makes it easy to select the correct one. This author has made a habit of
enclosing the extensions in parentheses ( ) so the extension portion is visible in
the lists.

CA will not allow saving 2 Customers with the same Name + Name Extension.
The **Balance** field shows the amount of money that this Customer currently
owes you.

We'll show the different Tabs of the Customers form and try to describe each
field - well, at least the ones that aren't self-explanatory.

_Chapter 10: Income Zone_ **263** CA _User Manual_


**10.2.5 Customer Info Tab**

**Company Name**
This field automatically fills in with the same text you enter into the **Name**
field. The author is not aware of anywhere in the system that this Company Name
is displayed or used other then here, but you may want to clear it if it doesn't
apply to this Customer.

**Contact Info fields**
The only fields in this section that the author knows are used anywhere else
except here (for your reference) are:

**Contact** (shows in the Search Customers dialog)
**Phone** and **Fax** print on Estimate and Invoice.
Possibly some of these fields will be used elsewhere in the future. You could
also have printouts customized to used these fields if you desire, see Sample of
PO printout on page 245.

**10.2.6 Billing Address**
The Address of the customer, it appears on
printed documents.

**Warning** : If the Customer has only one
address line (in addition to the Name and City /

_Chapter 10: Income Zone_ **264** CA _User Manual_


State / Zip) then always use the 1st line, as the address will not print properly if
you use the 2nd line and leave the first one blank. See sample shown, there is an
empty line between the name and address. If you use the 1st address line and not
the 2nd, then it prints correctly without the empty line.

Another common mistake beginning users make is to enter the Customer's
Name in the first line of the Bill To address. This results in the Customer Name
appearing twice, as the 1st line of the Bill To Address as seen on any document is
always the **Name** field.

CA has in internal list of US Zip Codes, instead of typing the city name just
enter the **Zip Code** and it will auto-fill the City and State for you. The City / State
can be manually adjusted if it is determined that the auto-filled entries are
incorrect.

**Shipping Address**
Use this only if your Customer has one or more Shipping Address, or the
Shipping Address is not same as the Billing Address. You can enter as many
different Shipping Addresses as needed.

**Note** : There are 2 small buttons that show + and -. The Left one (+) is **Add** ,
to create a new Shipping Address, and the Right one (-) is **Delete** , to delete a
Shipping address.

To Create a new Shipping Address click on the **+** button. The **Name** of the
Shipping Address will print on documents, so be sure to change it from the
default _Ship To 1_. The **>>** button between the 2 addresses copies the Billing
Address into the displayed Shipping Address. If you only ship to the Billing
Address, you don't need to create any Shipping Address, it will automatically fill
the Shipping Address same a Billing Address on documents. See sample
displayed here for entry of Shipping Address.

**Warning** : If you click the little “-” button, it will delete the displayed Shipping
Address with no warning message.

There is a **Default ShipAddr** checkbox below the Shipping Address entry. If a
Customer has multiple Shipping Addresses you can select which one will be at the
top of the list of Shipping Addresses for this customer. The remaining Shipping
Addresses should sort alphabetically by name.

_Chapter 10: Income Zone_ **265** CA _User Manual_


**Updating Addresses**
When you modify the address on an existing Customer or Vendor it will update
the address blocks on all OPEN documents for this name. This works on both Bill
To and Ship To addresses.

**10.2.7 Additional Info Tab**

**Type**
This Combo Box allows you to select Residential or Commercial. This has no
real affect anywhere, and is not used for anything except as a reference as far as
the author is aware. This may change in the future. Possible usage would be to
filter the Customer list for reports or creating mailing lists, etc. A second party
spreadsheet program named CA_Labels is available for printing labels using the
CA Customers and Vendors, in it the Type can be used as a filter for displaying
only Customers (or Vendors) of one type.

```
As of the current version this list can not be edited by the user.
```
**Default Terms**
When you create an Invoice, this is the Terms (see page 111 ) that fill in. The
Terms determine the Due Date for the Invoice, and the discount, if any.

**Default Rep**
If this Customer is serviced by an independent Sales Rep, select the Rep here
(see Sales Reps on page 113 ). This allows you to get a **Sales Analysis Detail By**

_Chapter 10: Income Zone_ **266** CA _User Manual_


**Item** or **Customer History** Report on sales made by a particular Rep.

**Price Level**
This is the Price Level that is used when a document is created for this
Customer. See Price Levels on page 130 for more details.

**Account No.**
If you assign an Account Number or Code to your Customers, enter it here.
The Account No. appears on the Invoice printout, and it can be searched for in the
Search Dialogs (pg 52 ).

**Credit Limit**
If you enter an
amount other then
0.00 here, then CA
will alert you when
you create an
Invoice that puts the
Customer's Balance
over this Credit Limit. An entry of 0.00 is equal to Unlimited Credit.

**No Charge Sales**
If this option is checked then CA will not allow Charge Sales to be made to this
Customer. Only Sales Receipts can be saved, not Invoices. (Saving Invoice can be
overwritten by a User with Admin permission, by confirming via question boxes
that appear.)

**Cash Customer**
If this is checked, then it will allow you to manually enter / edit the Bill To
(Name / Address) field of Income documents made out to this Customer. Used for
a **_Cash_** **Customer** , see Sales Receipt, pg. 294.

**Cards (button)**
This button allows access to the Stored **Credit Card** information for the
Customer. This enables your company to save your Customer's Credit Card
number and Expiration Date, if you wish to do so.

**Warning:** This feature has some legal strings attached! If you decide to store
credit card info, read the following carefully and make sure that the clerks /
employees using this feature understand it. The standards for storing and
processing credit cards are set by the **PCI Security Standards Council**.

- The credit card Number must be stored in an encrypted form. This is not
    visible to you, but within the database the card number is stored as a long
    string of apparently random characters. This prevents anyone who can
    access the database directly from reading the actual card number, the
    encryption algorithm that is build into CA must be used to convert it back to

_Chapter 10: Income Zone_ **267** CA _User Manual_


```
the actual card number. If you read the news regularly you'll find that it's
quite common for hackers to break into some company's database and steal
credit card and social security numbers, etc.
```
- It is **not legal** to store (save, or retain on record) the CVV code, which is the
    3-4 digit security code that is found on the back of the card (some cards
    have this number on front).
- It is required that the application (CA) can provide a log detailing the
    adding, editing, access and deletion of Cards. This is the biggest 'gotcha'
    for CA users. In order to comply with this requirement you will need to do
    the following: Each clerk / user must have their own Log-In user, and have
    **Allow Credit Cards** checked (See Users, pg. 125 ). The user must be
    logged in under their own name when accessing the Card info. This is so
    the system can track WHO added / edited / accessed the card. For this
    reason, the system's admin and guest users are not allowed to have access
    to the Cards.
- The Access of Credit Cards in the previous paragraph means access to the
    full credit card number. Once a credit card is in CA any user may apply the
    Card to a payment or Sales Receipt by clicking the Cards button on the
    respective screen and selecting the correct card based on the last 4 digits
    and the Expiration Date. But to actually view the full card number to enter
    it into a card machine you will need to be logged in as a user with card
    access.
- For security purposes there is no printout available that will show the full
    card number, you will need to enter the transactions from the number
    displayed on-screen.
In addition to the Customers screen, there is a **Cards Button** on the Receive
Payment (pg. 289 ), Sales Receipt (pg. 294 ), Sales Order (pg. 275 ) and Invoice (pg.
277 ) screens. On SO and Invoice the button is located by the Bill To Address, and
if you “Select” a card it will place the card info (last 4 digits, etc) in the Memo
field. On the others the button is located by the Payment # field, and will enter
the card info into the Payment # field.

The Cards button on the various screens all open the same dialog, which
shows the cards for the Customer that is on that document, and has buttons for
adding, editing, viewing and deleting Cards.

**Notes**
Use this to enter general notes about the Customer. This is for internal
reference only, does not print or appear anywhere else.

**Alert Notes**
Any text entered
here will display as a
pop-up note each time
you select this Customer
to create a new

_Chapter 10: Income Zone_ **268** CA _User Manual_


document.

Notes and Alert Notes can be accessed from the Invoice and other document
screens via the Alert Notes label.

```
Groups
See Org Groups (pg 342 )
```
**10.2.8 Taxes Tab**
Here you can select if this customer is charged Sales Tax (page 378 ) or not.
Each active Sales Tax Item (page 212 ) will be displayed here, with a check-box to
select if it is Exempt or not.

The setup shown here is rather complicated. The SALES TAX COSH is the
only one that is an actual Tax, the rest are Sales Tax Items created for tracking
different Exempt categories.

The
displayed
sample
shows what
you should
NOT do, here
we have
checked most
of the entries
as Exempt,
but left both
SALES TAX
and FARM as
applicable, as
this
Customer
happens to
be a farmer
that also
buys some
taxable (non-farm) Items. Only one of these should be left unchecked, to create a
document that is either exempt or not exempt. If you track different levels of
applicable taxes, such as State and City, using different Sales Tax Items, then you
would leave more than one unchecked.

The Taxable settings can be changed on each document and also on each line
item of a document, the settings made here are only what come up as the default
when you create a new document.

**Tax Exemption Info**
In version 2020.1 **Exemption ID** and **Expiration Date** fields where added. If
an Expiration Date is filled in then it will show an alert when you create a

_Chapter 10: Income Zone_ **269** CA _User Manual_


document for this customer that is past this Date.

Many states require that you have an up-to-date Sales Tax Exemption Form on
file for all your non-taxable customers. This allows you to set up an alert not
notify you when an exemption needs to be renewed.

**Warning:** this information is stored in the database as plain text, not
encrypted like Credit Card data. There may possibly be legal issues involved in
storing a Social Security Number or Employer Identification Number in here.
Click on the red **(Notice)** text on screen to read a disclaimer message.

```
10.2.9 Jobs Tab
Usage of this feature is described in Job Tracking on page 339.
```
```
10.2.10 Document History Tab
This works same as the Document History Tab for Vendors, see page 236.
```
This screen-shot shows filters applied to list only OPEN documents, which is
the default setting.

**10.2.11 Create Invoice button**
At lower left of of the Edit Customer screen is a Drop-Down
button labeled Create Invoice. Click on here to create a new
Invoice for the currently displayed Customer. If you click the
Drop-Down (or Right-Click the button) a menu will show that
allows you to create an Invoice, Credit Memo, Sales Order,
Estimate or Receive Payment for the current Customer.

**10.2.12 Create Vendor**
There's a **Create Vendor** option on on this button that will open the Vendors
form (pg 232 ) with name and address, etc., filled out same as this Customer.
Used to quickly add this person / company to your Vendor list.

_Chapter 10: Income Zone_ **270** CA _User Manual_


**10.2.13 Deleting / Merging Customers**
Clicking the **Delete** button at the bottom of the Customer Edit screen will
delete the current Customer. It will show a pop-up asking if you want to delete,
so you don't accidentally delete a Customer if you happen to click on the button.

If the Customer already has
documents then it is not
allowed to delete. Instead it
will show a dialog asking if you
want to **Merge** this customer
with another one. If you click
Yes a dialog will appear that allows you to choose which Customer to merge this
one with. The documents of the current Customer will be moved to the selected
Customer, and the current Customer is deleted. This is useful when the same
Customer is accidentally entered twice, and both have documents.

_Chapter 10: Income Zone_ **271** CA _User Manual_


### 10.3 Customer Bulk Edit.......................................................................................

Occasionally it becomes necessary to change some setting(s) in your customer
list that affects many or most customers, such as changing the default Terms (pg
32 ) because of a company policy change.

This is where Customer Bulk Edit comes in handy, it allows you to rapidly
make changes to customer settings based on current settings or other criteria.

```
This screen is accessed through Menu > Income > Customer Bulk Edit.
```
**10.3.1 Selecting Customer Criteria**
In the **Customer Criteria** section at top you select the options to specify
which customers will be updated.

In the displayed screenshot we've set the Customer Type set as _Residential_ and
have the Default Terms set as _5% Cash & Carry_. Only customers matching these
settings will be updated. Any criteria field that is blank will be ignored.

To match customers based on a Sales Tax setting select the desired Tax in the
**Sales Tax Filter** combo box. Check the **Is Exempt** check-box if you want to
match customers that are Exempt from the selected tax, otherwise leave it un-

_Chapter 10: Income Zone_ **272** CA _User Manual_


checked to match customers that are not exempt.

**10.3.2 Choosing Bulk Edit Fields**
In the Bulk Edit Fields section check-mark all the options that you want to
update, and set that option to the desired value.

In the screenshot shown we're updating the Default Terms of the matching
customers to _2% 10 Net 30_.

**10.3.3 Applying Updates**
When you click the **Apply** button at bottom a Confirm Changes dialog will
display that shows all the customers which will be updated.

If desired you can
un-check any
customers which you
do not want updated.

Click **Yes, I Agree**
to update all the
selected (check-
marked) customers.

_Chapter 10: Income Zone_ **273** CA _User Manual_


### 10.4 Estimate........................................................................................................

This is the 'root' document of the Income Zone, it is used to give your
Customer an Estimate on products or services you sell. Some users will refer to
this document as a Quote, there is a setting in Income Settings that allow you to
customize the Title for Estimate Printout (pg 139 ).

```
See the Invoice section on page 277 for general help.
```
The **Create Inv** button in the upper right converts the Estimate into an
Invoice or a Sales Order. To select the **Create Sales Order** (or **Create Purchase
Order** ) option, click on the small down-pointing arrow that is on the right side of
the **Create Invoice** text on the button. See the Converting Documents
(Importing) section on page 286 for help on the Import process.

There is a **Status** combo box in the Upper right that can be used to _CLOSE_ an
Estimate. When all lines are converted to a Sales Order or Invoice the Estimate
automatically becomes CLOSED, but sometimes it is desirable to close an old
Estimate (that was not approved) without deleting it. There is also a Close Old
Estimates utility (pg 144 ) that allows you to CLOSE all Estimates older than a
given date.

An Estimate does not affect your Inventory on Hand or P&L Report like an
Invoice does. See Posting vs. Non-Posting on pg 76.

_Chapter 10: Income Zone_ **274** CA _User Manual_


### 10.5 Sales Order....................................................................................................

This document is generally used for items that have been ordered, but are not
ready to be invoiced yet. Maybe if you have a mail order business someone will
open the mail (or take phone orders) and enter all the orders as Sales Orders,
then the SO is invoiced after it has been picked from the shelves and is ready to
ship.

In a manufacturing business the Sales Order would be used to enter orders,
which would not be invoiced until the items are made and shipped.

Data Entry is just like in an Invoice (page 277 ). The only difference is: A Sales
Order is a Non-Posting document (see Posting vs. Non-Posting on pg 76 ), it does
not affect your Inventory on Hand (it does display as **Qty On SO** ) and does not
show up as Income on the P&L Report like an Invoice does.

The **Create Invoice** button in the upper right converts the Sales Order to an
Invoice. A Sales Order can be split into multiple invoices if a partial order is
shipped / Invoiced. See Standard Form Buttons on page 38 for help with the
drop-down on this button. See Converting (Linking) Documents section on page
78 for help on creating an Invoice.

```
This document has a Status control that allows you to manually change the
```
_Chapter 10: Income Zone_ **275** CA _User Manual_


status to CLOSED even if the items are not all Invoiced.

The **Save** button's drop-down list has a **Save & Receive** option for creating an
Account Credit document for this Customer. See Advance Payments / Account
Credit On pg 385. Added v2023.1

_Chapter 10: Income Zone_ **276** CA _User Manual_


### 10.6 Invoice...........................................................................................................

This is the primary income document, the Invoice (bill) that you give your
customers. You must create an Invoice before you can receive a Payment (except
when using a Sales Receipt, see page 294 ). And you must receive a Payment
before you can make a Deposit, which you need to do in order to have money to
spend...

The sample displayed here was created using the Create Invoice button on the
Sales Order (page 275 ), to Invoice that Sales Order.

**Warning:** If you create a Sales Order, then modify the tax rate before
exporting it to an Invoice, the total amount will not be same, as it will calculate
taxes based on the Tax Item's rate, not what was used on the Sales Order.

A lot of the controls and their usage is covered in General Help on Forms on
page 29. We will try not to repeat too much.

_Chapter 10: Income Zone_ **277** CA _User Manual_


Here is a screen-shot of the Column Width / Position /
Visibility drop-down (see pg. 35 ).

**Applied / Owed**
In the upper right of this form it shows how much of
the Total amount of this Invoice has been Paid (Applied)
and how much is Owed. **Note** : These numbers are (for
some reason) reversed until you save the Invoice.

**Status Indicator**
In the center of the form you can see text saying
_TRANSACTION LINKED_. This indicates that this
document is linked to one or more other documents, either
an Estimate, Sales Order or Payment.

**Terms**
The Invoice can't be saved without selecting its Terms.
See Default Terms on page 266.

**Memo**
This is for internal reference only, does not print on
documents. If you convert a document, it will enter a
reference number in here for you. In this sample you can
see that this Invoice started as and Estimate #123, then
was a Sales Order #118 before becoming an Invoice. The Invoice Number is not
filled in yet, because the document was not saved at the time of this screen-shot,
see Document Number (Auto-Generated) on page 30 for more details.

**Totals**
At the lower right, just above the bigger buttons, it displays the Subtotal, Tax
Amount and Document Total for you. This re-calculates as you add and edit lines.

**10.6.2 Payments Button**
This button opens a dialog listing all the Payments that have been applied to
this Invoice. From this dialog you can open any one of the payments, or create a
new Payment (if the Invoice is not paid).

If no Payments have been applied it will open the Receive Payment screen so
you can process a payment.

```
10.6.3 ADD TAX
This button will re-set the applicable Sales Taxes for each line item. It will set
```
_Chapter 10: Income Zone_ **278** CA _User Manual_


Taxable / Exempt based on the settings for the Item and the Customer.

If the Item is not Taxable, then the line is not Taxable. If the Item is Taxable
then it checks the Customer, if the Customer is Taxable then the line is Taxable.
This applies to each individual active Sales Tax Item.

**10.6.4 REM TAX**
This Button removes all Sales Taxes. That is, it sets them all to Exempt
(Unchecked).

```
10.6.5 Payments (button)
This button does one of 2 things:
```
1. If one or more payment has been applied to this Invoice it will show a dialog
    listing all the Payments received. You can double-click on one to open the
    Received Payment.
2. If no payments exist it shows a dialog that allows you to receive a new
    Payment. This feature can only be used to create a payment in full, it does
    not allow receiving partial payment or applying discounts. If you want to do
    either of these things you can click on the **Open Receive Payment** button.
    If this Customer has other unpaid invoice(s) it will automatically open the
    Receive Payment screen instead of the dialog.

**10.6.6 Save & Receive**
The Save button on this form has a drop-down with a **_Save & Receive_** option.
This will save the current Invoice and open the Receive Payment screen with the
current Customer loaded.

```
This action can also be triggered by hitting the F12 key on your keyboard.
```
```
10.6.7 Line Items
Entry of Line Items in Table Control, or Data Table is covered on page 34.
```
Not all available columns are shown by Default, click on the little icon in
the upper right corner of the Table Control to show a list of all available columns
and which ones are visible (checked). See the picture of available Invoice
Columns earlier in this chapter.

```
Here is a listing of all the available columns.
```
**Item**
This is the Item Combo Box that is explained in detail on page 34. Enter an
Item Number.

_Chapter 10: Income Zone_ **279** CA _User Manual_


#### QOH

Quantity on Hand is a read-only field that shows the current quantity (Main
Unit) of this item in stock. This is valid only on Inventory Items, is blank on all
other Item Types.

**Location**
This read-only field displays the Item's Location, which can be a shelf / bin
number or something similar. Location is set in the Item's Inventory or Other Tab,
see page 197.

**Item #**
This is the Item Number that prints on the Invoice. Defaults to the Item
Number (page 187 ) of the Item selected, but can be modified if desired.

**Description**
Description of Item, as entered in the Item's Sales Description (page 177 ). This
is what prints on the Invoice, can be modified as desired.

**O'd**
Quantity Ordered - this shows the total quantity of this Item that was entered
on the Sales Order. Shows blank for any line that was not Imported from a Sales
Order.

**I'd**
The author has been unable to determine what this field represents. It always
shows 0?

**Job**
This allows you to select an open Customer Job (Jobs Tab, pg 270 ) or Company
Projects (pg 116 ) that this line applies to. Not available for Sales Tax Items.

**Unit**
This is the Item's Unit. See Units Tab on page 195 for more info. If an Item
has more then one Unit, it will use the Unit that is checked to be the **Def. Selling**
Unit, unless you change it here.

**Meas. Qty.**
This column is an extra multiplier that can be used as a linear measurement by
entering the piece length. This will then be multiplied against the quantity to get
a total price. An example of usage would be if you were selling cloth that you buy
by the Bolt and sell by the Yard, you might sell 2 pieces ( **Qty** ) of 4 Yards ( **Meas.
Qty** ) each, a total of 8 Yards for a single line entry.

This column is hidden by default, & does not affect anything unless a value is
entered. It was added at request of user(s) of CA, you should not use this unless
you're sure it's the answer to your problem and will make your life easier. If you

_Chapter 10: Income Zone_ **280** CA _User Manual_


do use it, you'll probably want a customized Invoice printout (see page 245 ).

**Qty**
The Quantity (count) of this Item you are selling. Enters 1 by Default, change
to any number, including decimal (partial) numbers such as .5 or 2.75, etc. Labor
is a good example of a partial unit, you might charge your customer .5 hr of labor
for repairing his chain saw.

Be careful not to sell part of something that is one piece, charging your
customer for 1/2 of a Honda Engine might make him happy (provided you're
giving him the whole engine), but trying to explain that Inventory figure to your
Accountant might not make you happy. Adjust the Rate if needed, but keep the
Qty real.

**Base Price**
A read-only field that displays the Base Price (page 178 ), which is the Selling
Price when No Price Level is selected. As a possible use, you might set the Base
Price to be the lowest price you can sell the Item for (or the Cost without any
markup), then it would be visible as a reference if the Customer (with a Price
Level) asks if a discount is available.

**Cost**
A read-only field showing the Cost of the Item.
**Note** : This column only available if current User has permission for the Items
Security Zone.

**Rate**
The Per Unit **Selling Price** for this Item (this line, this document). Auto-fills
based on the Item, Price Level and Unit selected, can be changed if desired,
including setting it to 0.00.

This field is accurate to 8 decimal places, which is enough to eliminate most of
the **rounding errors** that occur when you multiply the Qty by the Price.
Throughout CA, most Price fields will accept 8 decimal places, until the Total
when it is rounded to 2 decimal places (even cents). A lot of calculating occurs if
you are using prices based on markups off the Cost, possibly with different Units
included, which can result in an occasional penny or so difference from your
manually calculated price.

**Weight**
Display's this Line Item's Weight, for the Unit selected. Can be manually
edited or entered, see Weight, page 185.

```
Total Wt.
Read-only calculation of Weight x Qty, see Weight column above.
```
_Chapter 10: Income Zone_ **281** CA _User Manual_


```
Total
This read-only field displays the Total of this line, Rate * Qty.
```
**Notes**
This uses the same Pop-Up Dialog text editor that has been on the Vendor Bill
for a long time. See Notes (Line Item), pg. 243. Does not print unless your
printout is customized for it.

**Taxes**
This drop-down shows a list of all active Sales Tax Item s (page 212 ) in your
system. Check only the Sales Taxes that you are charging on this line. If the
settings in the Taxes Tab of the Item (page 190 ) and Taxes Tab of the Customer
(page 269 ) are correct, then this should be correct by default.

**S.O. / Est.**
This shows the source document where the line was imported from, if
applicable.

**10.6.8 Converting to Credit**
An Invoice cannot have a negative total. In v2020.1 a feature was added
where if you try to save a new Invoice with a negative Total it will ask if you wish
to convert to Credit Memo, and if you click Yes it will convert the document to a
Credit Memo before saving.

**10.6.9 Invoice Printing**
The Invoice is one of the most common documents that users want
customized. An attempt was made to implement a number of the most commonly
requested features on the "New Style" Invoice, and a number of settings allow
some of these features to be suppressed if desired, see Printing tab of the Income
Settings dialog on page 138.

The remaining Income document printouts (Estimate, Sales Order and Sales
Receipt) and the Purchase Order were match the format and features of the "New
Style" Invoice. In all documents the "Original Style" printout is still available
using the Print button's pop-up menu list.

**Watermark**
You can add a Watermark, or background logo / image to your Invoice. This is
done by saving the desired image as a PNG image named **watermark.png** and
adding it to the **Standard Reports** tab of the Report Manager (pg. 349 ).

If desired you can add a different Watermark for each different Customer Type
(p. 266 ). Just name the various images as **Residential_watermark.png** and
**Commercial_watermark.png** and add them to the Report Manager. If you have

_Chapter 10: Income Zone_ **282** CA _User Manual_


a **Residential_watermark.png** and a **watermark.png** entered, then Customers
that are tagged as Residential will get the Residential picture and all others will
get the watermark.png.

Depending on what word processor you're using you may require outside
assistance to create the watermark image. The image needs to be faded (semi-
transparent) so it doesn't hinder the readability of the text.

**Notes Line**
Sometimes you may want to highlight a note-only (no price) line on your
Invoice (or other Income document) to provide a break-point in the print. This
can be done by having a Notes Item where the Item Number is or starts with 2 -'s,
e.i: -- That line will then get a darker background.

Here is an Estimate that has a Notes line. Note that the Header is customized
as "Price Quote" using the Title for Estimate Printout setting (pg 139 ). The
document displayed was used to test the # of characters usable on printout.

_Chapter 10: Income Zone_ **283** CA _User Manual_


This shows how the standard Invoice printout in Classic Accounting looks.
This sample has a Watermark (pg. 282 ) on it, the watch picture in center.

_Chapter 10: Income Zone_ **284** CA _User Manual_


Here is an Invoice print when it was imported from SO, with some of the
options on Income Settings Printing tab (pg. 138 ) checked. Note extra columns.

_Chapter 10: Income Zone_ **285** CA _User Manual_


**10.6.10 Packing List**
One of the documents that can be printed via the Print button's drop-down list
is the Packing List. This document is available in both Invoice and Sales Order
forms, but can show slightly different information depending where you print it
from.

One of the differences is the title (header) of the print, which can be
customized in Income Settings (see Title for Packing List on pg 139 ).

**10.6.11 Converting Documents (Importing)**
The dialogs used for this process were replaced with a new one in version
2023.1. See Converting (Linking) Documents (pg 78 ).

**Creating Purchase Orders**
It is possible to create a Purchase Order from an Estimate or Sales Order.
Select Create Purchase Order from the **Create Invoice** button's drop-down
menu. This works same as creating a Sales Order or an Invoice, but it generates a
Purchase Order (in the Expense Zone). This will not CLOSE the document, you
still need to create an Invoice (or Sales Order) after the Items have been received.

When an Estimate / SO Item is exported to a PO, then the Vendor Part Number
is normally used as the Item Number, if there is any. There are some settings to
control exactly what happens, see Other Tab of Income Settings dialog, pg 137.

**10.6.12 Importing Items from other Documents**
You can also import additional items into an existing document.
On many of the document forms this is triggered by using the drop-down menu
(right-clicking) on the **Create <doc>** button at top right, there you will find an
option for **Import Doc Items**. On the Invoice form this is a button of itself that
does not appear until the Invoice is saved.

In v2023.1 the dialog(s) used for this process were replaced with a new one.
See Import Doc Items (pg 81 ).

_Chapter 10: Income Zone_ **286** CA _User Manual_


### 10.7 Credit Memo..................................................................................................

The Credit Memo ( **New Credit** ) is in the Invoice Zone under the Invoices
group, or in Income Menu. This looks similar to an Invoice, the difference is that
it is a Refund, or IOU to your Customer.

This will re-receive Items, if you create a Credit Memo for an Inventory Item
then it will reflect that Item as being returned (back in stock).

If you enter Sales Tax on a Credit Memo it will Decrease the amount of Sales
Tax you owe. Be careful when doing this, your state may have laws about how
you can or can't deduct from the Sales Tax you've charged.

When processing payments, Credit Memos are shown as negative amounts,
and will apply money against an invoice.

If a Customer has a Credit Memo that is equal to or Greater then an Invoice
that he/she owes, you can create a Payment of $0.00, check both the Invoice and
Credit Memo and they will be 'Paid'. If the amounts of the Invoice and Credit are
not identical you may need to manually adjust the figure(s) in the Payment column
to use only part of one of the documents.

You do not enter any quantities or prices as Negative Numbers to create a
Credit (although you can do so on an Invoice). Note that the **Owed** amount in the
upper right corner and the **Total** at the lower right both say _($51.00)_. The
parentheses indicate that is is a **Negative Number**.

_Chapter 10: Income Zone_ **287** CA _User Manual_


**10.7.1 Issue Refund**
You can issue a refund on a Credit
Memo by writing a check to the
Customer. An **Issue Refund** button will
appear underneath the Tax Region
selector along the top of the Credit Memo
form whenever applicable. You must save
the CM before the button will appear.

Clicking on it will
open the Issue Refund
form. In it you can select
how much to refund, the
Refund Date, the Memo
to appear on the check,
and the Bank account to
use. Any Bank account
can be used, including a
Cash account if your
refunding in cash.

Once you have made
all the proper selections,
click on the **Issue
Refund** button at the
bottom right to generate a Refund Check.

Print or otherwise assign a number to the Refund Check by recalling it within
the Banking Zone (pg 317 )

In the
Refund
Check, note
that it has
used _1200
Accounts
Receivable_
as the GL
Account.
This will
reduce the
amount of
your
Accounts Receivable, as well as reduce the balance of your checkbook.

**Note:** You can also apply the Credit Memo toward an Invoice belonging to the
same Customer, see Refunds on page 292.

_Chapter 10: Income Zone_ **288** CA _User Manual_


### 10.8 Receive Payment...........................................................................................

Receiving a Payment is the incoming money transaction, the money your
Customer pays you to pay his/her Invoice. The only way to increase your
checking account balance (except by making Transfers or Journal Entries) is to
receive Payments then Deposit them to the bank. After a Payment is entered, that
transaction appears in the Deposit form (Banking zone).

A Payment can be used to pay only part of an Invoice by adjusting the payment
figure for a line item (Invoice), and a single Payment can be used to pay multiple
Invoices. So far in CA it has not been possible to use a single Payment to pay
Invoices belonging to more then one Customer.

This screen has a Column Width / Position / Visibility widget (pg. 35 ) that
allows you to customize the displayed columns. Some columns are hidden by
default.

Here is a Payment being processed for a single Invoice, with no discounts
applied. Pretty simple.

```
Note: Some screen-shots and text in this section revised for v2023.1.
```
1. Select the Customer in the **Receive From** Name box. There are 2 settings
    toward the right, **Show Only Customers w/Balance** (hides all Customers
    that have a 0.00 Balance Due) and **Show Inactive Customers** (shows
    Customers in list that are no longer set as Active.

_Chapter 10: Income Zone_ **289** CA _User Manual_


2. Check the **Date Received** and make sure it's correct, change if not. This
    should be the day you received the money.
3. Enter the amount of the payment in the **Payment Amnt** field at top, and the
    **Payment Method** and **Pmt #** (check Number).
    ◦ Alternatively, you can Check the Invoices to pay first, this can make a
       difference in how the Discounts / Partial Payments are calculated.
4. Check the**?** column of each Invoice line that you want to pay.
5. If a discount is available it will automatically calculates and show a
    message. This only shows if the **Pmnt Amount** is filled in first.
    ◦ If The total amount
       due of the selected
       invoice sets the
       **Total Payments** to
       more then the
       **Pmnt Amount** ,
       then it applies the
       available amount,
       either $0.00 or a
       partial payment,
       and show a
       message.
    ◦ Make sure the
       **Discount** Amount
       is correct (0.00 is
       correct if there is
       no discount). If
       you manually
       modify the
       **Discount** , it will
       always recalculate the **Payment** amount as **Amnt Due** less **Discount**
       taken. This calculates even if the total Payment(s) will then exceed the
       Total Payment amount at top, so if you are applying a partial payment
       you will then need to manually update the **Payment** amount as well.
6. If there is a Discount, make sure the **Discount GL** is correct. This is the GL
    Account used for the Discount entry, see General tab of the Income
    Settings dialog (page 137 ).
7. Check the **Payment** figure in the last column of the Invoice line, to be sure
    it is correct. If only a partial payment is being made you can adjust this
    figure.
    ◦ The Total of the Applied **Payments** (the Payment column of the Invoice
       line), which is displayed in the **Total Payments** field at bottom, must be
       equal to the **Pmnt Amount** at top.
    ◦ The **Total Applied** to – or Paid on – the Invoice(s) is **Total Discounts +**

_Chapter 10: Income Zone_ **290** CA _User Manual_


```
Total Payments.
◦ The Difference field will show 0.00 if the Payment Amount at top
matches the total Payments applied, otherwise this shows the difference
between them. You cannot save a payment if the Difference is not 0.00!
```
8. Click on the **Save** button at bottom to save the Payment.

**View Inv**
Select (highlight, does not need to be checked) any listed Invoice or Credit
Memo and click this button to preview it. From the preview you can print if
desired, but be aware that printing from the Preview screen does not updated the
document's Printed status. This does not trigger a Save action like most Print
buttons do, you can use this prior to saving the Payment. This button added
v2020.1.

**Save & Print**
The Save button has a drop-down option to **Save & Print**. Selecting this will
Save the Payment, then print a copy of each of the Invoices that the payment was
applied to.

In v2020.1 key shortcuts were added, F11 will "Save & Print" and F12 will
"Save & Go Back".

_Chapter 10: Income Zone_ **291** CA _User Manual_


**10.8.2 Complex Payments**
Here is a Payment screen showing a payment that is doing several different
things. The Credit Memo is being used as part of the payment. You should
always select Credit Memos, before Invoices!

The Total Due on _2062-7_ was $122.20. A 2% Sales Discount is being applied
(the Terms were 2% 10 Net 30). $122.20 less $2.44 discount less $24.89 Credit
results in a payment (check received) of $94.87. This results in both the Credit
Memo being used and the Invoice being paid in full.

**10.8.3 10.8.3 Refunds**
A Credit Memo can be applied towards an Invoice using a **Payment Amount**
of 0.00. This will not show up available to **Deposit**. A Credit Memo can also be
refunded to the Customer using the Issue Refund button on the Credit Memo
(page 288 ) to create a check / payment.

_Chapter 10: Income Zone_ **292** CA _User Manual_


You can't create a payment for less than 0.00. To give a Customer a Refund
for a Credit Memo: Create a $0.00 Payment with a Discount of the same amount
as the Credit, and a Payment of 0.00. Set the Discount GL to the account used to
refund the Customer. Above is a Credit of $2.22 being paid out of the Petty Cash
account. This transaction will set the customer's balance to 0 and reduce the
_1020 Petty Cash_ account by 2.22.

Following is a view of change being given for a check that is more then the
amount due. Note that if you are returning money to the Customer then the
Discount amount entered must be negative.

**10.8.4 Over-payment / Down Payment**
You can receive payments without using them to pay an Invoice. This creates
an **Account Credit** document, which linked to a particular Customer. This credit
can also be "tagged" to one or more Sales Order, to be used to pay it when the SO
is converted to an Invoice.

This feature is explained in Advance Payments / Account Credit on page 385.
An Account Credit is an easy way to retain the over-payment for use later, or
refund to the Customer via Check.

_Chapter 10: Income Zone_ **293** CA _User Manual_


### 10.9 Sales Receipt.................................................................................................

This is a combination Invoice and Payment form that is designed to be used as
a **Point-Of-Sale** (POS) system at the counter of a retail sales establishment.

Here a sale can be recorded and a payment received in a single form. It also
includes a **Tender** feature for calculating change due to a Customer. You can not
process charge sales using Sales Receipts, only sales that are paid in full at time
of sale.

This form can be set up to print a Receipt using a **Thermal Roll printer**. A
compatible thermal printer is required, such as a **Star TSP100**. Use the Print
button's Print Button 's **<Edit Button Settings>** options (see pg. 40 ) to specify
the receipt printer and set the Print Option to PRINT_NO_DIALOG, otherwise it
will show show the choose printer dialog each time you print.

**10.9.1 Creating a Receipt**
Here we've made a sale of 6 Set of Metric machine screws to a Cash customer
(The _Allen Hoover Jr._ text was typed directly into the **Sold To** text box).

The basic entry is identical to an Invoice (page 277 ), except it has fewer
document option fields and no Ship To address.

_Chapter 10: Income Zone_ **294** CA _User Manual_


Like the other Income screens, there is a Status label and Printed check-box.
If the Sales Receipt's Status if DEPOSITED it means the payment has been
deposited to the bank.

```
10.9.2 Entering a Payment
There are 2 ways a Payment can be entered.
```
1. Enter the Payment Type and # in the fields above the line items, then **Print**
or **Save**.
2. Click on the **Tender**
button to open the Tender dialog.

Enter the Amount of the
Payment Received ($10 in this
example) or click the **Payment**
button to fill in the exact amount.
Next click the Button at bottom
that corresponds to the Payment
Type being used. These buttons
change to display the Payment
Types you have in Your system.
if you left the Print Receipt
checked, then it will print a
Receipt. **Close** will exit the
Tender dialog without creating a
payment or saving the Receipt.
Enter the number of Check
received in the Check / Ref #
field on here.

**10.9.3 Converting SR to Invoice**
If you create a Sales Receipt, then the customer decides to charge it instead of
paying right away you can click the **To Invoice** button at top right to transfer all
the data onto an Invoice.

You cannot use this feature after the Sales Receipt has been saved.
There are settings for Convert Sales Receipt to Invoice (pg. 140 ) where you
can set if converting a SR to Invoice is allowed for a Cash Customer (pg. 267 ).

_Chapter 10: Income Zone_ **295** CA _User Manual_


**10.9.4 Sales Receipt Roll Print**

A Receipt from a 2-1/4" Thermal Roll
Printer is shown here.

This version of the Roll receipt print is
build in, via the Print button's Drop-Down list
(see Print Button on page 40 ).

If you do not have a Logo entered, the
Company Name & Address will print instead.

If you want a customized receipt print
you'll need to contact your dealer.

_Chapter 10: Income Zone_ **296** CA _User Manual_


### 10.10 Barcode Scanning.......................................................................................

```
CA has some special features to optimize use as a POS system.
```
**10.10.1 Barcode Entry**
The Barcode (actual number / text represented by the barcode) must be
attached to each Item in CA. This is done in the Item Unit's UPC field. You can
click in the cell you wish to enter the barcode in then scan the barcode to enter
the numbers / text.

In order to add items onto a document via barcode scanning you must first
place the focus on (click in) the Barcode Scan Field (pg 37 ). This field turns

yellow when it has the focus. You can then scan your Item(s) and they will be
placed on the document.

**10.10.2 UPC Search Sequence**
When you scan a barcode it will try to find a matching entry in the UPC codes
you entered in your Items (Units). CA will search for a matching UPC code in
the following sequence. The first Match that is found will be used!

1. Checks for a Math Operation. See next section for details.
2. Searches for exact match of the barcode in a Unit's UPC field (pg 156 ).
3. Checks if the barcode matches the Pattern of any of the Price-In-Barcode
    patterns (pg 298 ). The patterns are checked top (first) to bottom (last) as
    entered. If a match is found, the UPC (U positions) is extracted and the
    Unit UPCs are searched for a match.
4. Searches for an exact match in the Item UPC Code (pg. 185 ). If a match is
    found here it will use the Default Selling Unit when an item is scanned onto
    an Income document.
5. Repeats #3, but searches in Item UPC Code (like #4) instead of Unit UPC.
6. If no match is found it will display a
    **Warning** message. If your computer
    or Word Processor is equipped with a
    speaker or beeper it will generate a
    tone when this dialog is displayed.
    The message should close if you hit
    the Space Bar on your keyboard.
**Special Note:** UPC Entries are not case
sensitive, any lowercase characters (a-z)
will be converted to uppercase (A-Z) for
matching purposes when scanning bar-codes. This applies to both the UPC
entered in CA and the Scan Entry being processed.

To use barcodes printed by electronic scales with the selling price embedded
in the code see Price-In-Barcode patterns on page 298.

_Chapter 10: Income Zone_ **297** CA _User Manual_


**10.10.3 Math Operations (scanning)**
There are some special features embedded in the Barcode Scan field to allow
rapid modification of a scanned entry.

Immediately after you successfully scan an item onto the document, you can
use the keyboard to modify the Qty and/or Rate of the Item you just scanned. The
purpose of this is to speed up the process by not requiring mouse usage, these
entries can be done with the number keypad on your keyboard. Always follow
these entries with an **Enter** to activate!

Note that multiple math operations can be performed on the same item / scan,
just use one then the next, doing an Enter between each operation.

```
Set Qty
```
. #To set the exact qty of the line type either a. (period) or # (hash tag), followed
by the quantity desired. Qty will accept decimal point, so **.14.5<Enter>** will set
the line's Qty to 14.5.

```
Add to Qty
```
+ Add an additional quantity to the existing qty. **+2<Enter>** will add 2 more to
whatever is currently in the Qty.

```
Subtract from Qty
```
- Subtract from the current Qty. **-1<Enter>** will subtract 1 from the line qty. **If
this action puts the line Qty at or below 0 it will remove the line from the
document!**

```
Set Rate
```
/ @ $ To set the Rate (price) enter any one of the following characters: / (forward
slash), @ or $ followed by the Rate to set. **/4.95<Enter>** will set the line's Rate
at $4.95. Using $ or @ is a lot more intuitive then / for the Rate, but / is the only
of these that is found on the number keypad.

```
Force New Line
```
\ Sometimes you may wish to force the next scanned item onto a new line rather
then add it to an identical item already scanned. To do this, type the \ (backslash)
character into the scan field before you scan. Do not hit Enter after the \, just
scan the next item. It will enter the scanned item on a new line on the document.
This character is not on the number keypad, usually above the Enter key on the
main keyboard.

**10.10.4 Price-In-Barcode patterns**
This feature enables CA to extract the Price from a barcode printed by a
Labeling Scales. These patterns are entered in the Item Settings dialog, see Item
Settings: Other Tab (pg 134 ). As many patterns can be entered as needed, each

_Chapter 10: Income Zone_ **298** CA _User Manual_


line is a different pattern.

This works by the barcode (or the numbers represented by the barcode) being
in a certain pattern. Rather then hard-coding all common patterns in CA you
need to enter your own patterns. For maximum flexibility a few features were
added that are not known to be standard barcode features.

Read this Barcode Scanning section for information on what sequence the search
is done.

Following are the characters that can be used to create a pattern:

- **U** = UPC code (Product Identifier, this is what is entered in the Item Unit's
    UPC Field (pg 190 ). This is required, the numbers at the U positions are
    used to search the database for a matching UPC number in the Item List.
- **P** = The Price, defaulting to 2 decimal places. For a pattern of
    XUUUUUPPPPPX a price of $12.50 would be 01250 (there are 5 P's, you
    need to supply 5 numbers for the price). You can change the decimal offset
    by adding <space> Px after the pattern, with x being the # of decimal
    places. An example of a 4 digit price: XUUUUUPPPPPX P4. For this,
    01250 would be $0.125.
- **Q** = Quantity, instead of specifying a Price you can specify a Qty. Actually,
    you could do both in one barcode, if you design your own and use a barcode
    type that accepts the required number of characters. Again, this defaults to
    2 decimal places. You can change this by adding <space> Q<number>
    behind the pattern, so XUUUUUQQQQQX Q0 would have No decimal
    places.
- **M** = Same as Q, except it specifies Measure Qty instead of Qty. Use
    M<number> to specify decimal places.
- **Numbers (0-9)** = Literal, exact match. Example: if the first 2 characters of
    your pattern are 65, then the barcode must also start with 65 to be
    considered a match.
- **X** = Ignored. A true EAN / UPC number has one or more Checksum
    numbers, which are used by the scanner to eliminate false reads. This is a
    variable, and must be ignored when matching the pattern to the barcode.

**Example / how it works:** You have a single Item in your system for "Deli
Sandwich". The pricing varies for different sandwiches and sizes. Suppose we
have that Item's Unit UPC set as 34345, and we've entered a pattern of
XXUUUUUPPPPPX. In order to be a 'match', the scanned barcode must have the
same character count (13). The U characters (positions 3-7) are then extracted.
If these numbers are 34345, it will match (find) the Deli Sandwich. The numbers
at positions 8-12 are then extracted and a decimal point is added 2 places from
the right. So if the 5 digits are 00695 then the price would be 6.95. When this
barcode is scanned onto a document (Sales Receipt, etc) CA will enter the "Deli
Sandwich" item and set the Line's Rate at 6.95.

_Chapter 10: Income Zone_ **299** CA _User Manual_


**Reloading patterns**
The patterns are loaded into local memory so CA doesn't need to do a
database lookup each time it does UPC lookups. If you update the Patterns it will
update the stored patterns on that machine, but not on any other networked
machines. To force a networked machine to reload the patterns from database
open the Item Settings on that machine and click Save & Close.

_Chapter 10: Income Zone_ **300** CA _User Manual_


### 10.11 Finance Charges..........................................................................................

**10.11.1 Finance Charge Settings**
If an Invoice is not paid by the Due Date, which is determined by the Terms
(page 111 ) of the Invoice, then you may want to charge your Customer an
additional fee, called a **Finance Charge**. In the Income Settings dialog (select
Income Settings from the Income menu) there are settings related to the Finance
Charge. Open this dialog and select the Finance Charge tab.

This tab contains settings that are used for calculating Finance Charges
(Interest) that you charge your Customers on overdue Invoices.

**Annual Interest Rate %**
Often called the APR, or Annual Percentage Rate, this is the rate that you
charge on overdue Invoices. A 24% APR is 2% per month.

**Minimum Finance Charge**
This is the LEAST amount that any finance charge will be, many businesses
will charge a minimum fee of $3 - $5 per month, to cover the cost of mailing the
Statement.

**Grace Period (days)**
The Grace Period is how many days after the Invoice is created before any
Finance Charges are applied. Often 30 days, but could be 45, 60, 90, etc.

_Chapter 10: Income Zone_ **301** CA _User Manual_


**Calculate Charges From**
This setting gives you the choice of _Due Date_ or _Invoice Date_ , this determines
which date that it starts calculating the Finance Charge from. The Due Date of an
Invoice is determined by the Terms that are selected for that Invoice.

**Finance Charge Item**
This selection determines which Item is used as the Finance Charge (the Item,
in turn, will determine which GL Account is used). Proper setup of this item is
required to keep you Accountant happy, see Other Charge Item (page 211 ) for
details on setup of this Item.

If you currently do not have an Item that is appropriate to use for Finance
Charges you can click the **Add** button to create a new Item. A new database will
automatically contain an Item named _FC_.

**Finance Charge Terms**
Specify the default Terms to use when you Assess Finance Charges (pg 302 ).
This setting added in version 2023.1.

**Use Short FC Description**
The text that is on the Finance Change Invoice shows a lot of detail about the
charges. If this results in too much text / information for your needs you can
check this option to show fewer details, which reduces the text on the Invoice.

**10.11.2 Assess Finance Charges**
To actually apply Finance Charges to an
Invoice, you need to create a **Finance Charge
Invoice** , which is a separate Invoice containing
the Finance Charge. This process is pretty simple,
as CA has a build-in form for doing this.

Click on the **Finance Charges** button in the
Income Zone, Invoices button row. This opens the
**Assess Finance Charges** form shown here.

If you hover your mouse above a row you can
see the details of all the invoices that are over due.

_Chapter 10: Income Zone_ **302** CA _User Manual_


This same text will print on the Invoice unless you check the **Use Short FC
Description** option in Finance Charge Settings (pg 301 ) of Income Settings
dialog.

**Assessment Date**
Select the Date that you want to calculate the Finance Charges up to. The list
in the Table Control will show all Customers that have a valid Finance Charge as
of this Date. Changing this date will change the list of Customers and the
Finance Charge Amounts.

**Tax Regions**
Here you select the Tax Region that are applicable for Finance Charges. If the
Customer is Exempt from Sales Tax, then no Sales Tax will be charged regardless
of this setting. A Finance Charge is generally Taxable, but it may vary from State
to State.

**Invoice Terms**
Select the Terms for this Finance Charge Invoice. An unpaid Finance Charge
will eventually generate Finance Charges of its own! The default terms to use can
be specified in Finance Charge Settings (pg 301 ) section of Income Settings.

**Sales Rep**
Select the Sales Rep to use on the FC Invoices. If the Require Sales Rep
option (pg 140 ) is checked you must select a Sales Rep here in order to generate
Finance Charge Invoices (otherwise an error will occur when CA attempts to save
the Invoices).

_Chapter 10: Income Zone_ **303** CA _User Manual_


**Selected**
In this column, select (click to check) all the Customers that you wish to create
a Finance Charge for. Sometimes you may want to give a certain Customer a
break and not create a Finance Charge. Use the **Select/Unselect All** check-box
at lower left to check or uncheck all the lines.

**Last FC Date**
This displays the date of the last time you created a Finance Charge Invoice
for this Customer.

**Invoices**
This column contains the text that will print in the Invoice's line item
description field. This text can be edited (new for v2023.1) by using F2 or
Ctrl+Enter to show the Multi-Line Text Editor (pg 35 ).

```
Over Due Balance
This is the total amount of all overdue Invoices for the given Customer.
```
**Finance Charge Amnt**
This is the amount that will be charged on the Finance Charge Invoice. It is
calculated per settings in the Finance Charge tab of the Income Settings dialog.
This number can be modified if you do not want to use the pre-calculated amount
for any reason. This column uses Calculator Cells, (added v2023.1) see pg 38.

**Assess**
Clicking this button (lower right) will generate the Finance Charge Invoice(s).
One Invoice will be generated for each Customer in the list that is Selected.

When you **Assess** Finance Charges, the Invoice(s) will be created. The
Invoice(s) can be viewed using the **View/Edit** button for Invoices, or more likely
you'll want to click the **Print** button in the Invoice button list and print all the
new FC Invoices.

Note that FC Invoices use a different Numbering Sequence from regular
invoices.

**10.11.3 Printing Finance Charge Invoices**
The easiest way to print FC Invoices is using the Batch Printing form (page
48 ). Otherwise you have to use the View / Edit Invoice, open each one and print
it.

_Chapter 10: Income Zone_ **304** CA _User Manual_


### 10.12 Statements..................................................................................................

If you make charge sales, you may need to send out an occasional reminder to
your Customers that they still owe you money. This reminder document is called
a **Statement**. Or maybe you have Customers that you make a lot of sales to, and
you have an agreement that the Customer will pay on a monthly basis, from the
Statement.

To create Statements click on **Statements** , the bottom button of the Invoice
buttons group. This opens the Statements form. Some new settings were added in
version 2023.1 and some more in 2024.1 – new features, read this section!

In the following text we will try to explain what each of the options on this
screen does.

```
Most of the check-boxes will "remember" their state.
```
_Chapter 10: Income Zone_ **305** CA _User Manual_


**Report Period**
The period End Date is used as the "Statement Date".
The period Start Date is used by several other options, see Show prior
transactions as 'Balance Forward' below and Print Invoices section (pg 309 ).

**10.12.2 Print Statement Settings**

**The following settings control the information that is displayed on a Statement.**

**Show Paid Invoices on Statement**
If this is un-checked then Invoices that have already been paid will not be
listed on the Statement, even if they are dated within the Report Period.

**Show Payment Activity on Statement**
If un-checked then the Statement will not display any Payments. If checked
then Payments that were made during the Report Period will show on the
Statement.

**Show prior transactions as 'Balance Forward'**
If checked then balance due of all Open transactions prior to the Report Period
**Start Date** will be summed into a single line labeled **Balance Forward**.

Prior to version 2024.1 the default behavior was same as having this checked,
and there was no option to disable it.

**Show Age instead of Past Due**
The Statement has a Past Due column showing the number of days past the
Due Due for each Invoice. The Due Date is calculated per the Terms selected on
the Invoice. If this option is checked, then the Statement will show the Age of the
Invoice instead, that is the number of days since the Invoice Date.

**Show Cust Alt Phone**
If checked then the Statement will include the Customer's Alt Phone instead of
Phone number. This is useful if you use the Alt Phone / Contact fields to store
Billing contact information, which is often different from the Sales contact.

```
Show Cust Alt Contact
Same as Alt Phone.
```
**Show Company Alt Phone**
Use this if you want your Customers to call a different number from your main
phone for Billing / Statement questions. You will need to fill in the Alt Phone field
in the Company Info form (pg. 110 ) to utilize this.

_Chapter 10: Income Zone_ **306** CA _User Manual_


**Suppress "Transaction History" warning**
If this option is NOT checked, and you print a Statement that is dated so the
Statement's Balance Due is not equal to the Customer's current balance due, a
block of red text will appear to the right of the Customer Name / Address stating
that this is a "Transaction History Report", along with the current balance due.
Some users did not care for the Transaction History warning so this setting was
added to allow disabling it.

**Show Sales Receipts**
If this option AND Show Paid Invoices on Statements are both checked then
the Customer's Sales Receipts that are within the Report Period will be listed on
the Statement.

```
This option is to allow showing full transaction history for each customer.
```
**Show Discount info on Statement**
If checked then a note showing available discounts will be displayed on the
Statement, if any discounts are available.

Special Note: Discount calculation is always done from current date, not from
the Statement Date. If you are mailing out Statements a few days into the month
but have back-dated the statement to the last day of previous month, then it
would make no sense to print an available discount that expired yesterday.

```
This is a new feature for version 2024.1.
```
**10.12.3 All Customers Statement Filter**

**The following options affect the output of "All Statements"**

Note that these options do not affect the list of names displayed in the
Customers section.

**Include if Any Transactions in period**
If checked then it will print a statement for customers that have a $0.00
balance, but have transactions in this statement period. This is useful if you send
a monthly transaction history to your customers, even if they have no balance
due.

```
Most of the following settings will override this setting.
```
_Chapter 10: Income Zone_ **307** CA _User Manual_


**Must have Transactions in Period**
If checked then then it will generate a Statement only for Customers that have
one or more documents dated within the Report Period, AND have an outstanding
balance. This is useful if you accumulate Invoices over the period of a month then
send statements (and Invoices) out at the end of the month.

**Must have Overdue Invoices**
If checked then the "All Customers" option will only include Customers that
have Invoices that are overdue. An Invoice is considered "Overdue" based on the
Due Date of the Invoice. (This was changed in 2023.1, previously it was using a
more complex calculation of "Overdue".)

**Must have Invoices older than (days)**
The "Must have Overdue Invoices" setting doesn't always provide the optimal
filter for some users. By checking this you can limit "All Statements" to only
include customers with one or more Invoice older than a given number of days.

**Customer Must Owe Money**
Checking this will eliminate customers with a Credit (negative) Balance from
being included in "All Customers" Statements.

```
Having this checked will eliminate statements like this one:
```
**Customer Must Be Active**
This is normally checked, it un-checked it will include In-Active Customers in
the "All Customers" output.

**10.12.4 Customers section**
In the Customers section is an Option Button that allows you to toggle
between **One Customer** and **All**. Beneath that are 2 options that control who
gets Statements. **Only Customers w/Balance** will prevent Statements from
being send to Customers that owe nothing - if this is Unchecked then it will create
a $0.00 Statement for all Customers that don't owe any money. You will probably
want this checked! If **Only Active Customers** is checked, then it will not create
a Statement for any Customers that are set as Inactive.

_Chapter 10: Income Zone_ **308** CA _User Manual_


If you select **All** then click the **Print** button at bottom, it will print Statements
for all Customers (controlled by settings). If you select **Only One Customer** then
the Name Combo Box beside it will become active and contain a list of Customers
(controlled by settings). Select the desired Customer in this list then click the
**Print** button to print a Statement for only that Customer. This is handy if you
only want to send statements to a few of your Customers.

If you create Statements using the All option it
can take some time, especially if you have a lot of
customers owing you money. A "busy dialog" will
display, showing that CA is working for you.
Consider what CA does and try to figure out how
much time it would to do all the Finance Charges
and Statements manually. It's really pretty fast!

**10.12.5 Print Invoices section**
Here you have options to print Invoices along with your Statements. The
Invoices will print in rotation with the Statements, that is it will print a Statement
then it will print all the Invoices belonging to that Statement. The options are
pretty self-explanatory, you can choose to print only Open invoices, or only ones in
this Report Period, etc.

**Save As PDF**
This is a new option for version 2023.1.
This allows you to save the individual customer statements as a PDF file when
you run "All Statements" (either Print or Preview). Use the **Browse** button to
select a Folder in your system to store the files to. It is recommended to use an
empty folder (create a new one if needed).

**Notice** : Statements are not saved in CA. If you want a copy for your records,
you must either save a printed copy for yourself or save a PDF copy.

```
Number of Copies
Specify the # of copies of each Statement to print. Default is 1.
```
**Same # Invoice Copies**
If this is checked AND you specified more than one Statement Copy AND you
specified a **Print Invoices** option, then it will print the same number of Invoice
copies as Statements.

If not checked then it will print only one copy of each Invoice, but x copies of
the Statement as specified in Number of Copies.

_Chapter 10: Income Zone_ **309** CA _User Manual_


Here's a Statement printout. This is pretty basic, it doesn't show much activity.

_Chapter 10: Income Zone_ **310** CA _User Manual_


## Chapter 11: Payroll Zone.........................................................................

The **Payroll** menu and zone have only limited functionality. Only Employees
and Timecards (and required supporting parts, like Pay Periods and Payroll Items)
are currently available. The payroll zone was created in the early days of CA, but
was never enabled.

_Chapter 11: Payroll Zone_ **311** CA _User Manual_


### 11.1 Timecards......................................................................................................

Timecards are functional, but currently only as a stand-alone document. The
main purpose for them is to enable tagging labor to a Job, and to get a printout of
hours worked for a pay period.

```
Timecards are used to enter a time worked record (document) for Employees.
One Timecard is a document for One Employee for One Pay Period.
```
**11.1.1 Time Details**
Here is some information on the fields to be entered in each row. Each row is
a period of hours worked. Depending on how your business operates you may
enter only one line for each day, or you may break it down to multiple lines per
day to account for break times or to break it into multiple jobs.

**Entry Date**
The Date that this line's entry occurred. This date must be within the Pay
Period range.

_Chapter 11: Payroll Zone_ **312** CA _User Manual_


**Item**
This enables you to enter a Service Item from the standard Items list. This
is likely intended to be used for the purpose of billing customers for labor, but at
the present it is not used in any manner. Entry of this item is optional.

**Payroll Item**
This is the Item that provides the basis for the Employee's pay. The exact rate
of pay is set in each Employee's Earnings list, which carries over to the Rate
column of this form.

It is necessary to enter a Payroll Item. The original setup of this form required
this to be filled in and it was left that way to provide better data when moving
forward with payroll.

**Hours / Qty**
The number of hours (or Qty of Units) worked or to be charged. The Timecard
is set up so you can either manually enter the exact hours here, OR enter Start
and End Time, which will then calculate this field's value.

**Description**
An optional field to add notes pertaining to this particular entry. Prints on the
Timecrard.

**Start / End Time**
Entering the Start and End time calculates the Hours / Qty. Note that there is
no provision for making an entry that spans multiple days, Start and End time are
both in the same calendar day.

**Rate**
The per hour rate paid to the Employee. At the present time this information
is used only for Job Profit & Loss.

**Job**
This allows you to tag a time entry to a Job and have it show as an expense on
that Job's Profit & Loss report.

Be aware that at present this only uses the rate given in this Timecard, while
the actual hourly cost of an employee's labor is significantly higher than the
Employee's hourly wage rate. You should consider adjusting this number to
reflect the actual cost-per-hour for the labor rather then what you pay the
Employee.

_Chapter 11: Payroll Zone_ **313** CA _User Manual_


### 11.2 Pay Periods....................................................................................................

A Pay Period defines the Start and End
dates of one Payroll period (paycheck).

The **Bonus Pay Period** option has no use
at time this was implemented (v2020.1).

When a Pay Period is marked CLOSED it
tags all the Timecards for this period as
CLOSED as well.

_Chapter 11: Payroll Zone_ **314** CA _User Manual_


### 11.3 Payroll Items.................................................................................................

There are a lot of options available when setting up Payroll Items, but most of
them are not used at the present. It was necessary to activate this in order to
make Timecards functional.

_Chapter 11: Payroll Zone_ **315** CA _User Manual_


### 11.4 Employees.....................................................................................................

Employees can be added / edited just like Customers (pg. 263 ) and Vendors
(pg. 232 ).

Employees have an **Eligible 1099** setting on the **Pay Info** tab, and will show
on the 1099 report if checked.

**11.4.1 Pay Info / Earnings**
In order to use Timecards it is necessary to add one or more Payroll Item to
the Earnings section in Pay Info tab.

The lower section of Additions, Deductions has no use at the present time.
Also, there is no functionality to generate Paychecks as the option displayed
here seems to indicate.

_Chapter 11: Payroll Zone_ **316** CA _User Manual_


## Chapter 12: Banking Zone......................................................................

The Banking Zone is where you control your Bank Accounts and keep track of
your Checking Account balance.

Checking (page 321 ) allows you to create and Print checks. For **printing
Checks** with CA you need QuickBooks ® compatible 3-part voucher style laser check blanks
with 1-check-per-page and check-on-top. See Printing Checks on pg 324 for details.

Register (page 318 ) is a form that allows you to view all of the entries (documents / transactions)
that occurred in any of your GL Accounts.

When you Pay Bills (page 256 ) it creates a **Bill Pay Check** that appears in the Checking section.
This Bill Pay Check must be printed or edited to assign the proper check number to it. When you 're
Reconciling your Checking Account (pg 332 ) you will want the check numbers correct so you can match
them to your Bank Statement.

Deposit (page 326 ) allows you to Deposit your Receive Payment s (page 289 ) into your Checking
account. If you skip this step then your Checking balance will go further below zero each time you
write a check or pay a bill.

Transfer (page 330 ) allow you to Transfer, or move, money from one GL Account to another. You
might use Transfers to make some of your Opening Balance of Accounts (Initial Setup) (page 98 ).

_Chapter 12: Banking Zone_ **317** CA _User Manual_


### 12.1 Register.........................................................................................................

This is a general purpose tool for viewing all the transactions of any GL
Account. Select the GL Account desired, and it opens a table view of all the
transactions of that account along with a running balance.

The Register was completely recreated in version 2023.1, and further refined
in 2024.1. It is considerably faster in loading data than it was before.

Viewing the Register is a good way to trouble-shoot, if you aren't sure if the
transaction you entered did what it was supposed to do, check the GL Accounts in
question and see what happened. If you make Transfer (pg. 330 ) or Journal
Entries (pg. 128 ) check the Register to make sure the accounts adjusted in the
desired manner. If not, try swapping the To / From accounts.

When you click the **Open Register** button the form opens without any data
loaded. You need to choose the desired GL Account using the Combo Box in the
upper left corner.

To look up an account that is no longer active check the **Include Inactive** box.
**Special Note:** This account picker will search like some other combo boxes,
but you need to hit the Tab key, or click on the Refresh button to load the list.

The entries are sorted by Date, with oldest entries on top. The initial view,
when the list is loaded, has the list scrolled all the way down, showing the most

_Chapter 12: Banking Zone_ **318** CA _User Manual_


recent entries.

At the bottom, the **Ending Balance** shows the current Balance of the Account
The Register can be sorted like many other tables, click on a column header to
sort by that column.

At the bottom is a label that shows how many records are loaded, as well as
buttons for viewing or opening the listed documents. (new for 2024.1)

**12.1.1 Printing The Register**
There is a Print button at the bottom that will print the contents of the
Register in a list format. Clicking this button will bring up a dialog that allows
you to print the entire register, or only the transactions in a given date range.

**Hint** : Use Print Preview (page 49 ) before you actually print, so you don't
accidentally print some 100+ page report!

**12.1.2 Saving The Register To A Spreadsheet**
This is not really a "feature" of Classic Accounting, but due to general
functionality of Java's table control it is possible to dump the entries of the
Register into a spreadsheet.

1. With the desired data loaded, click on any row of the Register.
2. Select the entire register using the shortcut: Ctrl+a
3. Copy the selected data to the system clipboard with shortcut: Ctrl+c
4. Open a spreadsheet file (new or existing). You may not close (exit) Classic
    Accounting.
5. Click on a cell to paste to. This will become the top left corner of the pasted
    data.
6. Paste the clipboard contents with the shortcut: Ctrl+v
    Some formatting and column width adjustments will be in order.

**This process can be done with any table control in Classic Accounting!**

**12.1.3 Changing Cleared Status**
Once a GL Entry has been Reconciled (see Reconciling your Checking
Account, pg 332 ) the related document (Check, Deposit, etc) is marked as
**Cleared** and can no longer be deleted.

Sometimes it is necessary or desirable to modify a document after it has been
marked Cleared, say you have a Check that you need to edit the GL Accounts
after it has been reconciled:

1. Open the Register screen, selecting the Checking (or other) account that
    you reconciled.
2. Find the check or other document(s) in question and un-check the "Cleared"
    checkbox.

_Chapter 12: Banking Zone_ **319** CA _User Manual_


3. Click on the Save button at bottom before closing this screen, to update the
    document's status.
4. Now the document will be editable again. Make the desired changes
    (sometimes this involves deleting and re-creating the document).
5. Open the Register again, and select the correct GL Account.
6. Find the document, and check-mark the "Cleared" checkbox again.
7. Click the **Save** button at bottom before existing or loading another account,
    otherwise it will not update the document status and it will show up on
    Reconciliation screen again.

If your document is an Invoice that is Paid and the Payment has been
Deposited and the Deposit has been Cleared... Well, that's a long chain, but you
need to start by removing the Deposit's Cleared status same a the Check
described above, then you can delete the Deposit, Delete the Payment and
(finally) Edit the Invoice. After changes are made you need to re-create all the
documents, taking particular care to get the dates correct (same as they were
originally).

A Vendor Bill is about same as an Invoice – remove Cleared from the Bill Pay
Check, Delete the Bill Pay Check then Edit the Vendor Bill. When done recreate
the Pay Bill and mark it Cleared.

**Warning** : Unless you're really sure you know what you're doing (and even
then probably not) you should not change the total amount of a Cleared
transaction, because otherwise your Checking account balance will be altered.

The typical use case is to change the Expense (or other) GL Account that was
used, or maybe modify the Customer or Vendor of a document that was incorrect.

_Chapter 12: Banking Zone_ **320** CA _User Manual_


### 12.2 Checking.......................................................................................................

This section allows you to write checks directly from your Checking Account to
any Vendor OR Customer. When creating a Check you use GL Accounts rather
then Items. This works, but it creates a transaction that will not show up on the
**Purchase Analysis Detail by Item** and **Vendor History** Reports. If you want
detailed reports and for best search results in CA Search you should probably use
Vendor Bills with Line Items (page 252 ) whenever possible, even if it's something
you're paying right away.

The **New Check** button opens the **Checks** form which allows you to write a
check.

**Bank Account**
CA can track multiple payment accounts for you, Checking, Cash or Credit
Card. At top right is a drop-down (combo box) where you can choose which
payment account to use for this check. This list includes all Bank accounts
(Checking or Cash) plus Credit Card accounts, see Usage of various Account
Types (page 94 ) for more info.

**Pay To**
In the Combo Box above **Pay to the Order of** you can select any Vendor or
Employee to write a check to. The text appearing in the Vendor's Print On Check
As field (page 233 ) is what will print as the Check's "Pay to the Order of", for
Employees it's the **Check Name** field. The text that actually prints as the Pay To

_Chapter 12: Banking Zone_ **321** CA _User Manual_


The Order Of on the check appears below the Combo Box, and if the Vendor has Is
Cash Vendor checked (pg 235 ) then you can manually edit this text. The same
applies for a Customer that is set as Cash Customer.

If you need to write a check to a Customer click on the **Show Customers**
check-box above the name selection combo box, then the list will include all active
Customers.

**Check Amount**
After filling in the Pay To name (Vendor / Employee / Customer) and making
sure the date is correct you should fill in the total amount of the check in the **$**
field below the date. The **Total** box at bottom right shows the sum of all the
Account Entries in the lower section of check form, that Total must match with
the Check Amount entered at top before the check can be saved.

**Account Entries**
Making line entries on the check is like entering Account Items on a Vendor
Bill (see pg. 253 ). You select the **GL Account** (usually an Expense account) and
enter the **Amount**. The **Memo** column can be used for entering a description, it
prints on the check stub. A **Job** column is available if you're doing Job tracking
with CA, if you are not using this feature you can hide the Job column using the
Column Width / Position / Visibility widget at top right of the table (pg. 35 ).

Vendors have a Default Purchase Account (pg 233 ), if this is filled in then the
first line of Account lines will auto-fill the first Account line for you. This can be a
time saving feature for any Vendor that normally uses a certain account.

**Additional Fields**
The Memo field prints on the Check, in the lower left corner.
There is a Status label to the right of the Memo field that shows the Check's
status. It will not display on a **_New_** check, but after it has been saved it will show
**_Open_** , and once the check is reconciled the Status changes to **_Cleared_** (then the
check cannot be deleted or modified anymore except by Changing Cleared Status,
see page 319 ).

```
Above is a picture of a check after it has been printed (note the check
```
_Chapter 12: Banking Zone_ **322** CA _User Manual_


number). Clicking the Print button automatically saved the check (note the **Open**
status).

Also note that the Checking Account's balance has updated to reflect the
deduction made by this check.

**Check Number**
No Check Number is assigned to a check
until it is Printed. Clicking on the Print
button will open a **Check Number** dialog
where you can modify the Check Number if
needed. CA keeps track of the Check
Number, but if you use several checkbooks,
such as some laser checks and some hand-
written book checks, with different number
sequences then you must be careful to enter the correct number here. See
further notes on Using multiple check number sequences.

Clicking the **OK** button will open the Print dialog. In this dialog, click **Print** to
print, or click **Cancel** to not print and assign the Check Number anyway.

You can also print Checks from the Banking Zone using the **Print** button in the
Checking button group. This is a Batch Printing form as explained on page 48 ,
except it has additional fields at the bottom for selecting the **Bank Account** you
are printing, and the **Starting Check Number**. Double-check them both before
clicking the **Print** button! This view shows that it's time to reorder checks, see
Banking Settings on pg 148.

**Using multiple check number sequences**
CA tracks the last used check number to allow sequential numbering. When a
check is printed, it assigns the next check number and updates the internal
setting. (only sometimes though, read further)

If you change to an entirely different number, this sequence will follow the
number you used last. (Each different Bank account tracks it's own number
sequence, though.) For my own business I mainly use **Laser Checks** , but I also
have a hand-write checkbook with a completely different number sequence that I
use occasionally. In order to assign the proper numbers to the hand-written
checks without resetting the Next Check Number setting (so it remains correct
for my Laser Checks) I save the check ( **Ctrl+S** works fine) then click the **Is
Printed** checkbox and manually change the number at top..

_Chapter 12: Banking Zone_ **323** CA _User Manual_


**It works like this:**

- The Batch Print screen ALWAYS updates the next check number.
- Printing from the Check screen itself will update the next check number
    ONLY if you click the **Print** button or check the **Is Printed** box BEFORE the
    check is saved (see Saving Documents, on page 45 ).
- If a check is first saved without a number assigned, you can then Edit it,
    check **Is Printed** and modify the check number without updating the Next
    Check Number.
- All Bill Pay Checks are saved w/o a number assigned, so the only way to
    print a Bill Pay Check so that it DOES update the Next Check Number is
    through the Bulk Print screen.

**Printing Checks**
If you want to use CA to print Laser Checks you need to get the check blanks
through your Bank or a Print Shop. The style of checks to order is “QuickBooks 3-
part with Check On Top”. This is an 8-1/2” x 11” (letter size) paper with
perforations to tear into 3 pieces. The top portion contains the Check, the other 2
parts are stubs that show the line-items that you entered on the check. The stub
printout is slightly different on a Bill Pay Check vs. a regular Check. Laser
Checks come with the check number printed, so you'll need to specify a starting
check number. You can't just print your own number on the check, as the line of
funky looking numbers along the bottom, which includes the check number, are
printed with a special ink for scanning purposes.

If you mail checks, or want a proper-fitting window envelope to use with the
Checks, you should get Check Envelopes from the same source as the Checks.
Check Envelopes are usually double-window, are different size then the common
#9 and #10 double-window envelopes, and vary from brand to brand.

There is an additional check print, if you open the Print Button's pop-up menu
(pg. 40 ) you'll have the option for **Check Voucher Alt_1** , which has slightly
different positioning / alignment of the Name / Address / Signature. If the default
printout is not putting the text in correct position, try this print. If it prints better
you can set it as the default using <Edit Button Settings>.

There is also an option to **Use Alt_1 Check** on the Check Bulk Print screen.
The normal practice is to tear off the bottom stub and retain it for your
records, maybe staple it to the bill being paid, then fold at the remaining
perforation and send the other stub along with your payment so your Vendor can
see what's being paid.

**Note:** Computer-printable checks are called Laser Checks, because you're
supposed to use a Laser printer to print them. It is possible to print checks with
an Inkjet printer, and your bank will most likely accept it, but injet prints will
smudge / blur when wet, and are easier to alter then a Laser print.

_Chapter 12: Banking Zone_ **324** CA _User Manual_


**Printing Signature on Checks**
CA can can print your signature directly on the check.
First create an image file of the desired signature named
**check_signature.png** , then go to **Menu > Reports > Report Manager**. On the
Standard Reports tab click **Add Report** and change the Type of Files from _Jasper
Report Files_ to _All Files_ , then select the signature image and click OK. Click **Save
& Exit** to close dialog and refresh reports.

You may need to adjust the amount of white space around the edges of your
**check_signature.png** file to get it to print at the right position.

It appears that not all brands of checks have the signature line in the same
place. There is an "Alt 1" version of the check printout build into CA, if the
amounts and signature doesn't print at the correct location with the default
version try this one. If you still can't get your signature to print in the correct
place contact your dealer to get a printout modified so it will work for you, or
read the instructions on how to do it yourself in Changing position of Check
Signature on page 373.

**Attachments on Check**
To the bottom right of green Check area there is an Attachments button (see
pg 344 ). Button added version 2023.1.

```
A Line Links button (pg 38 ) is also at this location.
```
When you use the Pay Bills feature (pg 256 ) a Bill Pay Check is generated.
Instead of the GL Accounts list it will display a list of the Vendor Bills that were
paid with this check. You cannot edit this list from the check, if it needs to be
changed the only option is to delete the check and re-create it.

_Chapter 12: Banking Zone_ **325** CA _User Manual_


### 12.3 Deposit..........................................................................................................

After you have received one or more Payment, when you deposit that money in
the bank you also create a Deposit in CA. Normal practice is to create the CA
Deposit before you take the money to the bank, as it allows you to print a Deposit
Summary or Deposit Ticket, which adds all the Payments together for you and
allows easy double-checking to make sure all Payment entries are correct.

When you click on **New Deposit** a **Select Payments to Deposit** dialog will
open which displays all available (undeposited) Payments.

All payments are **Selected** by default, un-check any that you do not want to
Deposit, or use the **Select / Unselect All** box at bottom left to uncheck all
payments then manually check the ones you want to deposit.

You can select / un-select a 'block' of payments by selecting (highlighting) the
rows to modify, then right-click on **Select / Unselect All** checkbox to set the state
of all the highlighted rows to opposite state of the Select / Unselect All check-box.
To rapidly highlight rows Click on first row of desired block, then Shift+Click on
last row

_Chapter 12: Banking Zone_ **326** CA _User Manual_


**12.3.1 Pay Method filter**
If you're making Deposits to several Bank Accounts, you must create a
separate Deposit for each one, with the correct Payments Selected. Click on the
**Pay Method** Combo Box to open a list of available Payment Methods. Select the
desired **Payment Method** to list all payments of that method, or the blank (which
is the default) to list all undeposited Payments. This is used to easily separate
Check, Cash or Credit Card payments to deposit them.

**12.3.2 Select Payments for Date**
This field allows easily check-marking all the payments for a given Date. This
should make it easier to process large numbers of credit card payments, where
you want each days receipts on a separate deposit. Instructions for use:

1. Select a Pay Method to filter by, if desired.
2. Enter the desired date in the date field at bottom of dialog.
3. Click on the **Select** button. This will do 2 things:
    1. Check-mark all the payments in dialog with the date that was
       displayed.
    2. Advance the date by 1 day, so you're ready to do the next day's
       deposits.
4. Repeat steps 2 and/or 3 as needed for your use.
5. Click the **OK** button to create a Deposit of the Selected payments.

This table also has a Column Width / Position / Visibility widget (page 35 ), as
does the table on the main Deposits screen.

**12.3.3 Create Deposit**
Once
you've
selected the
desired
payments to
put on
deposit click
the **OK**
button to
create the
Deposit.
Here is a
view of
payment list
filtered to
Cash
payments.

_Chapter 12: Banking Zone_ **327** CA _User Manual_


```
The Deposits form is pretty straight-forward.
```
**1.** Select the Bank Account you want to **Deposit To.**
2. Make sure the **Deposit Date** is correct.
3. Enter a note to yourself in the **Memo** field if desired.
4. **Notes** field is just a larger field to add notes to yourself. The text entered in
    Memo field is search-able from the View / Edit screen, but Notes are not.
5. Use the **Payments** button to add/remove Payments to this Deposit if not
    correct.
6. Click **Print** (or **Save** , if you don't wish to print) to save the Deposit to the
    database.
    1. To print a Ticket rather then a Summary right-click on Print and select
       **Deposit Ticket**.

```
An Attachments button (pg 344 ) was added to this form in version 2023.1.
```
**12.3.4 Deposit Ticket**
You can print either the Deposit Summary, or a Deposit Ticket if you have the
correct form to print it on.

_Chapter 12: Banking Zone_ **328** CA _User Manual_


The Deposit Ticket will print on a QuickBooks style Deposit Ticket. This is a
letter-sized paper with a tear-off deposit ticket at top and the rest of the page is a
summary for your records.

You must order these through your Bank, a Print Shop or other seller of
Checks. They need to be printed with your business name / address and bank
information, including routing and account number. If you purchase Tickets and
the printing does not align properly please contact your Classic Dealer for a
customized printout.

_Chapter 12: Banking Zone_ **329** CA _User Manual_


### 12.4 Transfer.........................................................................................................

A Transfer is an easy way to move money from one GL Account to another
within CA. From an Accountant's viewpoint, you should probably use Journal
Entries (page 128 ) instead, but a Transfer is easier to understand, and is the most
common way to transfer money between Bank and Asset Accounts.

By careful use of Transfers and Journal Entries it's possible to straighten up a
severely messed up accounting system. **_It's also an easy way to severely mess
up an accounting system_**.

For our sample company, we determined that we had $48.75 in our Petty Cash
drawer when we started using CA, on Mar 1, 2015. Here we're making a Transfer
of 48.75 **From** _3000 Opening Balance Equity_ **To** _1020 Petty Cash_ to make our
Petty Cash account in CA show the correct Balance. See Opening Balance of
Accounts (Initial Setup) on page 98.

The **Memo** is for entering a note concerning this Transfer. **You should
always do this** , as it can be very difficult to determine the purpose of a Transfer
at a later date, if there is no Memo to tell you.

In v2020.1 a Notes field was added, and a **Print** option that allows printing a
record of the transaction for paper filing purposes.

If you make a Transfer to GL Account _1090 Undeposited_ Funds then the
Transfer will be available to Deposit (page 326 ).

```
When depositing to 1090 Undeposited Funds you can use the Pay Method
```
_Chapter 12: Banking Zone_ **330** CA _User Manual_


and **Pmnt #** fields to show the correct Check / Ref# on the Deposit.

If you **Open** or **View / Edit** Transfers, it opens a **Search for Transfers** dialog.
Most Transfers have a habit of setting the **Status** as _COMPLETED_ as soon as it is
saved, so you will need to check the **Show All** option at bottom left to view it.

The **Search Text** field allows you to filter the Transfers to find the one you
want. Here's where proper entries in the Transfer's Memo field comes in handy,
as the Search finds text in the Memo. See Searching a list on page 52 for help
with Search Text.

In version 2023.1 an Attachments button (pg 344 ) was added to the Transfer
document. It is at the top right of the form.

_Chapter 12: Banking Zone_ **331** CA _User Manual_


### 12.5 Reconciling your Checking Account.............................................................

Reconciliation is accessed through the Menu Bar, General Ledger Menu (page
129 ).

Reconciliation is the act of confirming that your (checking account) balance
matches the balance that your bank is showing. Your bank sends a monthly
**Statement** shown all the transactions that occurred in your account. In CA you
will use the Reconciliation form to match those transactions with the ones you
entered in CA, to make sure you entered all the transactions correctly.

Select the Bank Account to reconcile
in the Select Account dialog.

In the form that appears there are 2
**tabs** (above the table) labeled Deposits
and Withdrawals. In the **Deposits** tab
all of the Deposits will appear and in the
**Withdrawals** tab all of the Checks
(including Bill Pay Checks) will appear. Transfers and Journal Entries may appear
in either tab, based on if it was a deposit or payment transaction.

_Chapter 12: Banking Zone_ **332** CA _User Manual_


**12.5.1 General check-list for Reconciling**

1. Make sure the **Reconciliation Date** is set later than the bank statement's
    Ending Date. It is best to give it a few extra days in case you accidentally
    dated some transaction wrong. Only transactions dated On or Before the
    Reconciliation Date will be shown in the lists.
2. In the **Statement Balance** field at bottom enter the Ending Balance from
    your Bank Statement. (If you forget this step you can enter the balance at
    any time.)
3. Go through all the transactions shown on your bank statement, search for
    each one in the appropriate list (Deposits / Withdrawals), and if you find it,
    check it (click on the cell in the **Cleared** column).
    ◦ Search tips if you can't find a transaction:
       ▪ The Date shown on the reconcile screen is likely the date your wrote
          the check, and it will probably not match the date on the bank
          statement, which is the date it cleared the bank.
       ▪ You can sort the lists by any column just by clicking on the column
          header (like **Ref #** , **Org** or **Amount** ). This can help find one
          transaction among many. Click the same column header repeatedly to
          "un-sort" it again.
    ◦ If there is a transaction on your statement that is not listed on the
       Reconcile screen then either it has not yet been entered, or the
       Reconciliation Date needs to be set to a later date.
       ▪ To add missing transactions, or modify incorrect ones, you can click
          the **Leave** button. When it asks if you want to save click Yes and it
          will have all your check-marks intact when you open the form again.
4. After you've found and checked all matching transactions, the amount in the
    **Difference** field along the bottom should be 0.00. If it is then you can
    complete the reconciliation by clicking on the **Reconcile** button at the
    bottom.
    1. The remaining (unchecked) transactions should be items that have not
       yet cleared the bank as of this statement.
    2. If you have matched and checked all the transactions on the statement
       and the difference is still not 0.00, then some entries are incorrect or
       missing in Classic Accounting.
       ▪ Check that there are no old transactions from previous statements in
          the Reconcile list, if there are they should be checked.
       ▪ Double-check that you have the correct amount entered in Statement
          Balance field.
       ▪ Check that there are no bank fees lurking on your statement that you
          failed to enter in CA.

_Chapter 12: Banking Zone_ **333** CA _User Manual_


3. To force it to balance and complete the reconciliation you will need to
    create an adjustment. Use a Journal Entry to do this. **Warning:** After 2-
    4 month of using Classic Accounting and doing reconciles it should no
    longer be necessary to do adjustments. If it still is you are likely making
    mistakes somewhere.
    1. Before leaving the Reconcile screen make a note of the Difference
       amount (+ or -)
    2. Create a new Journal Entry (Menu > General Journal > Journal
       Entries...).
       - Make sure the Date is on or before the Reconcile Date you are
          using.
       - Enter the checking account on the first line.
          ◦ If the difference is positive enter the difference amount in the
             Credit column.
          ◦ If the difference is negative, enter it in the Debit column, but as
             a positive number.
       - On the second line enter the same amount in the opposite column
          (Debit or Credit). If you don't know which GL Account to use, then
          use 3000 Opening Balance Equity.
       - In the Memo or Notes field make a note of why you are creating
          this Journal Entry.
       - Save the Journal Entry.
    3. Go back to the Reconcile screen. The Journal Entry should be
       available to check-mark in the appropriate tab, which should change
       the Balance to 0.00.
    4. Now you should be able to complete the reconcile by clicking the
       **Reconcile** button.

If it does Reconcile (the Difference is 0.00), that means Classic Accounting has
the same Checking balance as your Bank does. If it does not, then you likely have
made a mistake somewhere. Either some transaction you entered is not same as
the bank's, or the bank has a transaction you didn't enter in CA. You can click the
**Leave** button to exit and access other parts of CA, and it will retain your entered
balance and check-marks.

When you do a successful Reconcile it will generate a document for you. If
you wish to keep this document you will need to print it or save it as a PDF file, as
there is no way to recall this exact document later. See Print Preview on page 49
for details on creating / saving a PDF file.

There is a **Reconciliations** report in GL and Accountant Reports (see page
370 ) that allows you to recall the details of a prior Reconcile. This report is
different from the one generated by the Reconcile screen.

_Chapter 12: Banking Zone_ **334** CA _User Manual_


Once Checks are Reconciled they will have a status of **Cleared** and are not
editable anymore. If absolutely necessary the Cleared status can be manually
removed or added by checking / un-checking it in the Register (see Changing
Cleared Status on pg 319 ).

At the bottom of lists there is a **Select All** checkbox. If you know that your
reconcile system is up-to-date and the last reconcile was correct, it may be easier
Select All of the Deposits and/or Withdrawals, then un-check the ones that are not
on the Statement.

Along the bottom of the lists are labels that show the count and total of the
selected and unselected entries.

_Chapter 12: Banking Zone_ **335** CA _User Manual_


## Chapter 13: Other Features.....................................................................

This chapter is for various miscellaneous features in Classic accounting that
don't have an entire chapter of their own.

_Chapter 13: Other Features_ **336** CA _User Manual_


### 13.1 CA Search......................................................................................................

CA Search is opened by selecting CA Search from the Reports Menu, or with
the **Ctrl+F** key shortcut.

CA Search is a Dialog that opens on top of CA at almost the full size of CA.
While the Search screen is open you can't access any other CA features. The
search screen retains all its data and settings when closed and reopened.

It is used for searching Items and other history in CA by entering criteria such
as Date Range, Document Type and/or Status, Customer or Vendor and by
matching user-inputted search text.

Using CA Search is largely self-explanatory, but following is a list of some
shortcuts and features you may wish to know about.

- To update the displayed data do one of the following:
    1. Click the **Search** button.
    2. Hit the Enter key when focus is in one of the yellow search boxes.
    3. Hit the **F5** key.
    4. Hit the **Ctrl+R** key combo.
- Type text in the yellow search boxes to find matching text. This search is
    very broad, it may include a lot of entries you aren't looking for.

_Chapter 13: Other Features_ **337** CA _User Manual_


- The Search Only Fields will cause the 1st (left) search text box to look ONLY
    in the specified field for matching text.
- To view the contents of a cell, either Right-Click or Ctrl+Click on it.
- To open the Document pertaining to the currently selected row in the table
    either hit the Enter key, click the Open button at bottom or Double-Click on
    the table row.
- To open / edit the Item of the currently selected row click on the Edit button
    at bottom.
- To switch between the Detail and Summary modes either click the Mode
    button at top or hit Ctrl+Enter while in one of the yellow search boxes.
- The Summary mode is fairly simple, not as many options as the one in the
    stand-alone version of CA Search. Its primary purpose is to show $ and Qty
    totals for the given search criteria.
- The Detail search is limited to showing only the first 10,000 rows.
- Hitting the down arrow key on the keyboard while in a yellow search box
    will move the focus to the table.
- Searching is much faster when a Doc Type is selected, which searches for
    only one type of document, like Customer Invoice.
- Any and all search criteria may be empty, backspace the combo boxes to
    clear them.
- Security settings apply, to view Expense documents the currently logged in
    user needs to have Expense Zone security clearance, etc. You can bring up
    the log-in dialog by hitting Ctrl+L. There is no visible warning about
    security clearance, it just doesn't show anything the current user doesn't
    have clearance to see.
- If you can't find what you want, check the Date, Name, Document Type and
    Document Status settings, - clear if needed. Also consider that the
    currently logged in user may not have sufficient clearance to see
    everything.
- The lines for Bill Pay Checks will show the Payment Account used in the
    **Doc Item #** field and the Vendor Bill(s) paid with it in the **Description**
    field. Right-click or Ctrl+Click on Description to see everything, as it may
    be multi-line text.
- To close the dialog use your choice of Ctrl+G, the Close button or the X at
    top right of the dialog.
- **Entering a Document Type, Date Range or Name will significantly speed up**
    **the search process.**

The **Copy Doc** button was added in version 2023.1, see Copying & Pasting
Documents on page 84.

_Chapter 13: Other Features_ **338** CA _User Manual_


### 13.2 Job Tracking..................................................................................................

Jobs is a feature that was requested by contractors, but can be utilized by
other businesses as well.

- The intended purpose is to be able to track the income and expense from a
    particular Job. CA has a Profit & Loss report per Job.
- A Job is attached (belongs) to a Customer. Each Customer may have
    multiple Jobs. Customer Jobs are entered via the Jobs Tab of the Customer
    Edit screen (pg 270 ).
- The "Jobs" setup is also available as “Company Projects”, see Company
    Projects (pg. 116 ).

The **Search** button and the text box beside it allow you to search / filter the
Jobs list. You can select a Job and click **Edit** , or just double-click on the Job to
open the Edit Job dialog (same as Add Job)

At bottom right is a **Reports** button, you can select the Summary or Detail
report to the left of the button, and if you click on the drop-down of the Reports
button you can select between viewing the Selected Job, Open Jobs or All Jobs.
These Reports are also available from the Reports screen, but the options
available there won't allow you to print a report for a single job after it is
COMPLETE. (The Job list in the Parameters dialog only shows OPEN Jobs.)

**13.2.1 Creating Jobs**
Create a new Job by going the desired Customer Edit screen, click on the **Jobs**
tab and click the **Add New** button. A dialog pops up which allows you to enter
the **Job Name** , **Start Date** (auto-fills today) and **Notes**.

_Chapter 13: Other Features_ **339** CA _User Manual_


Leave the **End Date** empty – once you fill in the
End Date, the Job is considered COMPLETE.

Once a Job is complete it disappears from this
screen, unless you click the **Show All Jobs** option at
bottom left.

**13.2.2 Create Job From Document**
On Estimate, Sales Order and Invoice forms
there is an **Add Job** button. Click this button to add
a new job to the customer selected on the document.

**13.2.3 Tagging Income and Expenses to a Job**
After a Job is created, you attach Income and Expense records by selecting
that Job on the desired document's line items. A **Job Column** is available in line
items of All Income and Expense documents, Checks, Inventory Adjustment and
Timecards. The job is entered per line item rather then for the entire document,
select the appropriate Job for each line item.

In the Line Items table, the Job will auto-fill when the next new line is added, if
you select it once (but can be changed or removed). This auto-fill feature is not
available on GL Entry table in Vendor Bill and Check.

**13.2.4 Editing Job Entries**
The **Edit Jobs** button on the Vendor Bill form (pg 250 ) allows editing the Jobs
attached to the Vendor Bill after the Vendor Bill has been Paid.

Clicking this button on a PAID Vendor Bill will open the dialog displayed here
and allow you to set, edit or remove the Job entries.

_Chapter 13: Other Features_ **340** CA _User Manual_


**13.2.5 Job Reports**
There are 2 places where you can view the Job P&L reports, in the Jobs screen
(in Customer Edit, where you add / edit jobs) and in the Financial Reports section
(pg 353 ).

If you do not want to use the Jobs feature, you will probably want to hide the
Jobs column on the document Line Items. For instructions on this, see Column
Width / Position / Visibility (pg. 35 ).

The Job P&L reports show the Cost of Inventory Items as an Expense when the
Item is placed on the Invoice, not when it is on the Vendor Bill.

_Chapter 13: Other Features_ **341** CA _User Manual_


### 13.3 Org Groups....................................................................................................

This feature is for creating Groups, or Lists, of names for purpose of
generating mailing lists or creating reports of sub-groups of customer or vendors.
The term Org is probably a shorthand for "Organization", it is the name of the
database table where all the Names are stored in.

**The basic idea is:**

- You create one or more Group(s)
    ◦ Each Group is for one type of name (org): Customers, Vendors or
       Employees
- Each Group can have one or more names attached to it.
    ◦ Each name (Cust / Vend / Emp) can belong to one or more Group(s)
- Certain reports have a filter that allows you to limit the report to one or
    more Group(s).
    ◦ This includes a "Customer Mailing List" report.

#### ◦

```
13.3.1 Adding and Editing Groups
Select the Menu option Company > Org Groups Editor
```
_Chapter 13: Other Features_ **342** CA _User Manual_


```
The top section is for Adding, Renaming or Deleting Groups.
```
1. Choose the type of Group at left, Customer, Vendor or Employee
2. Use the **Add** , **Edit** and **Delete** buttons to open an editor dialog for Org
    Group.
    1. A group can be made Inactive. To show it again click on the **Show**
       **Inactive Group** check-box.

```
The bottom section is for bulk editing a single Group at a time.
```
1. To add / remove names in bulk select the desired Group then click on **Load**
    **Group** button.
    1. This will load all names of that type in the list boxes below.
       1. The Left list is the names belonging to this Group.
       2. The Right list are names not in this group.
    2. To include inactive names in the list check-mark the **Show Inactive Org**
       box before loading.
2. Move names from one list to the other.
    1. Click on a name to select (check-mark) it.
    2. Use > or < button to move all the check-marked named from one list to
       the other.
    3. Use the >> or << button to move ALL the names in one list to the other.
    4. Use the **Search** text box to quickly find names. This search will show
       matching phone numbers, city, state and zip as well as Names.
       ▪ You can also do multi-criteria matching by separating each phrase to
          search by a %. Example: To search for all the "Yoder" (name) in zip
          code 44654 (Millersburg, OH) enter your search as: yoder%44654
       ▪ If there is a single unknown character you want to match use _
          (underscore) instead of %. A single character (can be a space, etc)
          must be present to match the _, unlike % which will also find matches
          where there is no character there. "Joe _ Yoder" will find "Joe R
          Yoder" and "Joe M Yoder", but not "Joe Yoder" or "Joe AM Yoder". "Joe
          %Yoder" will find all 4.
    5. Use **Select All** and **UnSelect All** buttons to check or un-check all names
       in a list.
3. Click on **Save** to save the Group, or **Cancel Edits** to not save.

**Choose Groups from within Customer / Vendor Edit screen**
On the Additional Info Tab (pg 234 ) of Vendor and Customers (pg 266 ) you will
find a **Groups** list showing all the Groups available for that Org Type (Customer
or Vendor). Check or un-check the desired groups then **Save** the Customer /
Vendor to update.

_Chapter 13: Other Features_ **343** CA _User Manual_


### 13.4 Attachments..................................................................................................

Attachments allows you to save external documents such as PDF or Excel files,
etc to a CA Document, Customer, Vendor or Item.

- To prevent the database, and the database backup files, from becoming too
    big Attachments are stored in your computer's file system rather than
    within the Database itself.
- Create a folder dedicated to the CA Attachments. In the Per Machine
    Settings (pg 114 ) tab of the Company Options dialog select this path in
    **Path for Attachments Folder**.
    ◦ If you have multiple computers on a network you will need to use a
       shared file location for your Attachments.
- Within this folder CA will store your files in a cryptic numeric-named folders
    / files hierarchy. This is intended to discourage manually adding / editing /
    removing files, as those changes would not be recognized by CA.

Attachments are access via the Attachment button that is found on most
document screens, and on Customer, Vendor and Item Edit screens.

- If No attachments are present the button looks like this:
- If Attachment(s) are present the paper clip icon becomes Green:

**13.4.1 Using Attachments button / dialogs**
Clicking on an
Attachments button
will open the
**Attachments For:**
dialog shown here.
This dialog lists all
attachments linked
directly to the Org /
Item / Doc that it was
invoked from.

**Show All**
Clicking (check-
marking) the Show
All box at bottom left
can show additional
attachments, as noted
here:

_Chapter 13: Other Features_ **344** CA _User Manual_


- If displaying Org attachments it will also show all Attachments belonging to
    Documents of this Org.
- If displaying Doc attachments is will also show Attachments belonging
    directly to this document's Org (Customer / Vendor). But not Attachments
    belonging to other documents.
- If displaying Item attachments this option is disabled.

**Adding Attachments**
You can add a new Attachment by dragging and dropping a file from your file
browser onto the main Attachments dialog (previous). This action will open the
dialog below with the attachment name and other information filled in.

The **Add** button will open an additional dialog for adding / editing an
attachment.

You can click **Browse File** to open a file browser where you can choose the
file to attach. The file path and name will fill into the text box at top.

You can also drag the file out of your file browser and drop it onto the darker
top section. If this doesn't want to work for your try pausing a moment and
holding the file on the drop area before releasing it.

The **Attachment Name** is what displays in the Attachments list. This defaults
to the file name, but you can rename it to anything you wish. (Hint: _Parts
Schematic_ is a lot more descriptive than _SCAN_001234.PDF_.

```
The Notes field is just to allow you to enter notes for future reference.
```
_Chapter 13: Other Features_ **345** CA _User Manual_


**_Delete original file_**
When you Save the attachment the file is copied to your Attachments
folder. If you check-mark this before hitting Save it will delete the original file
when saving, otherwise the original will remain as it is.

This check-box always starts out as un-checked, but if you check it, it will stay
that way until CA is closed.

```
Clicking Go Back will discard any changes and not save.
```
**Editing Attachments**
For existing attachments you can open this dialog by selecting the desired row
then clicking the **Edit** button.

You can also open the Edit dialog by Right-Clicking on the attachment row.
On this dialog you can change the Attachment Name and view / edit the Notes.
The dialog will also display some information such as the original file name, the
name of the user (that was logged in) that added the attachment, and the date it
was attached.

**Deleting Attachments**
If you click the **Delete** button it will permanently remove the file from the
Attachments folder.

```
Right-clicking on the Delete button will provide 2 additional options:
```
- Restore to Original Location
- Save to Different Location
    Both of these options will enable you to delete it from the Accounting system
and still retain the file.

**Open / View Attachments**
Clicking on the **Open** button, OR double-clicking on the attachment row, will
open the file for viewing / editing. This uses the system's default application to
open the file.

Right-clicking on the **Open** button will also provide a **Save As** option that
allows you to save a copy of the file elsewhere without deleting it from CA.

**Copy File Path**
By clicking on an Attachment line you can copy the Attachment's current
location (path) to the system clipboard with **Ctrl+C**.

This overrides the table's internal Copy feature, it may be necessary to hold
down the C key a moment rather than just tapping it to make it work. A status

_Chapter 13: Other Features_ **346** CA _User Manual_


message will display along the bottom of the dialog (just above the buttons) if the
copy was successful.

**13.4.2 Attachments for Document**
If you Delete a document that has Attachments, those Attachments will still
remain in the system, but will "change ownership" so they belong to the Customer
/ Vendor of the document instead.

A document needs to be saved before an Attachment can be added, because
the attachment is linked via the document's ID, which is not assigned until the
document is saved to the database.

**13.4.3 Attachments for Item**
Item attachments can be accessed from within document forms! If you select
an Item Row in the document then Right-Click on the Attachments button it will
open the Attachments For dialog so you can view, add, edit and delete
attachments for that Item.

_Chapter 13: Other Features_ **347** CA _User Manual_


## Chapter 14: Reports Zone.......................................................................

This Zone contains buttons for viewing all available reports. Most of the
buttons will open some kind of dialog with various input prompts for Date Ranges,
Filters, etc. for the report. Some of the more important reports are: **Sales Tax
Liability** , **P&L Standard** , **Balance Sheet Standard** , **Customer Aging
Summary** , **Vendor Aging Summary** , **1099 Report**. The **Vendor History** and
**Customer History** reports are quite powerful for researching history of sales and
purchases (this is where you'll really wish you had used Vendor Bills with Line
Items for all purchases, instead of just using Checks). If you go to the process of
entering and maintaining all your Assets in CA, the **Visual Balance Sheet**
provides an interesting view of your company's overall value (balance sheet) over
a period of one year.

This screen uses a different Tab for each type of report (Financial, Income &
Receivables, Expense & Payable, Inventory and GL & Account).

_Chapter 14: Reports Zone_ **348** CA _User Manual_


### 14.1 Report Manager............................................................................................

If you're using Classic Accounting for your business record-keeping you may
eventually decide to have some of the printouts (referred to as **reports** ), such as
the **Invoice** or **Sales Order,** customized, or that you need some completely new
report that is not included in the standard CA reports.

Customizing the standard printouts can usually be done by your Classic dealer,
he/she will have the proper **Jasper Reports** editor software to do so. While
creating a completely new report is not a trivial task, your dealer may be able to
create one for you, or connect you with someone who can.

Clicking
the **Report
Manager**
button opens
the **CA Report
Manager**
dialog, which
allows adding
customized
reports to
override the
standard CA
reports
( **Standard
Reports** tab),
and also add
new reports to
the **My
Reports** tab of
the Reports
zone ( **My
Reports** tab).

To add a report to the current tab, click the **Add Report** button at bottom left.
A file picker will open that allows you to select one or more file, which will be
added to the list when you select **Open** on the file picker.

This file picker supports Multi-Selection (pg 57 ), you can select and open more
than one report at a time. There is also a Files of Type option at bottom that
allows you to show All Files instead of just .jrxml files. This can be used to add
graphic files used as watermarks, like show in the list above, or similar.

_Chapter 14: Reports Zone_ **349** CA _User Manual_


Clicking on the
**Remove** button will
remove the selected
Report(s) in the current
tab. You can also use
Multi-Selection on this
list of reports, if desired,
to remove more then one
at a time.

**Note** : Files added or
removed from the lists
are not actually copied
or deleted until you click
**Save & Exit** , you can
click **Cancel** at any time
to exit without making
any changes. Clicking
**Save & Exit** will also run
the Clear Report Cache
option, so you can test
the new report(s) right away.

**14.1.1 My Reports**
Any .jrxml reports added
to the My Reports tab will
show up as a button on the
My Reports tab of the
Reports Zone. The shot
here shows a report named
SalesTax.jrxml that was
created per customer
request. It has options for
Cash or Accrual basis,
Summary or Detail and
grouping sales per state.
This report may possibly be
available on request.

Clicking the **Reload My
Reports** button on the
Reports screen will rescan the MyReports folder for reports and add / remove
them from My Reports tab of the Reports Zone. This action runs automatically if
you use the Report Manager button to modify the reports. If there are no .jrxml
reports in **reports_custom/MyReports** directory then there will be no My
Reports tab on Reports screen!

_Chapter 14: Reports Zone_ **350** CA _User Manual_


There are a lot of different things to deal with when creating reports for this
list. People interested in creating reports can contact Conservative Technology
Solutions or Joseph Miller for information on available parameters, etc. Here is
some basic info:

- To keep a report, such as a sub-report, from not creating a button have the
    name start with _
- When using sub-reports or other embedded files the path is
    ◦ For Standard Reports: **reports_custom/<report.jrxml>**
    ◦ For My Reports: **reports_custom/MyReports/<report.jrxml>**
- Standard reports w/sub-reports should always check reports_custom first,
    then reports, for the desired sub-report.
**Reports installed by CA Report Manager should remain intact when CA
is updated, and can be removed at any time.**

_Chapter 14: Reports Zone_ **351** CA _User Manual_


**14.1.2 Jasper Reports Font Extensions**
When creating custom reports sometimes it is desired to use a specific **Font**
that is not available in the system as a standard font. Even when a Font is
installed on the computer Jasper reports don't always recognize and utilize it.

Jasper Reports supports adding fonts via a Font Extension package. If the
desired Font is available as a **True Type Font** (.ttf) your CA dealer or the
developers can create a JasperReport Font Extension file for it.

There is a setting named Path for Font Extensions Folder (pg 116 ) in Company
Options dialog. Create a folder in your file system to contain your font extension
files and select it as the Font Extensions Folder. Place your font extension file(s)
in this folder then restart Classic Accounting. Your reports should then be able to
utilize these fonts.

Note that this setting is per machine, you can create the font extensions folder
in a shared location if you wish, but you need to set the correct path on each
machine.

_Chapter 14: Reports Zone_ **352** CA _User Manual_


### 14.2 Financial Reports..........................................................................................

Financial Reports is what Accounting is all about. These reports show the
activity and value of your business.

The **Detail** reports are used mainly for trouble-shooting, when trying to figure
out where the numbers are coming from. Generally, they provide too much detail
to be useful for getting the big picture.

_Chapter 14: Reports Zone_ **353** CA _User Manual_


**14.2.1 Profit & Loss Standard**

A P&L is always for a **Period of Time** , see start and end dates in header.

The first section shows **Income** , the money received.
The second section shows the **Cost of Goods Sold** , how much the goods you sold cost you.
This gives the **Gross Profit** , which is Income less COGS
A common cause of confusion is the **Inventory Variance** in this section, which
shows up if you use Inventory Items. The Purchases account(s) give you the total
amount of purchases made. Purchases Plus Variance is the total Cost of the
Inventory Items that were sold in this period. In order to get accurate (and easy)
numbers here you should have a SET of Purchase and Variance accounts for
Inventory Items, and you should not use that Purchase account for Non-Inventory
purchases.
Inventory Purchase and Variance accounts will show a breakdown of where
the number comes from, Inventory or Non-Inventory items. (new for 2024.1)
The third section shows **Expense**.
**Net Income** is you **Gross Profit** less **Expense**
The **% of Total Income** column is each line's total as a % of the Total Income.

_Chapter 14: Reports Zone_ **354** CA _User Manual_


**14.2.2 Balance Sheet Standard**

A Balance Sheet is always for a specific **Point In Time** rather then a Time Period

The **Assets** section shows the money, equipment and inventory you have.

**Liabilities** shows how much money you owe to other people and businesses.

**Equity** is the difference, your total **Assets** minus your total **Liabilities**.

_Chapter 14: Reports Zone_ **355** CA _User Manual_


### 14.3 Income & Receivables...................................................................................

These reports get information about the Items you've sold and the Customers
you sold them to. Basically information on the Income Zone of CA. We will briefly
describe them and show samples of a few of the more common ones.

```
The button layout of this form was revised a bit in version 2023.1.
```
**14.3.1 Open Document List**
Shows all Open documents of a selected type. Also has option to limit to a
specific Customer. Note that there is a corresponding report in the **Expense &
Payable** section

_Chapter 14: Reports Zone_ **356** CA _User Manual_


**14.3.2 Document List By Period**
A list of Income Documents within a chosen Time Period. The only option is
the Report Period and what Document Type(s) to show.

**14.3.3 Document Details By Period**
A list of Income Documents within a chosen Time Period with (optional) Line
Item data. Can select what Document Type to show and if show only Open or All
documents.

**14.3.4 Items On Open Sales Orders**
A report for finding out what Items are currently on Sales Orders. Has
parameters to choose for Item, Customer and Preferred Vendor.

```
14.3.5 Items On Open Estimates
Same as Items On Open Sales Orders, but for Estimates.
```
**14.3.6 Item Sales Trend Analysis**
A Reorder style report that shows sales history for past 1, 3, 6, 12 and 36
month, and attempts to estimate how much product you will need for a given
period in the future (1 – 12 month) based on past sales.

**Disclaimer** : This report is not warranted for any purpose. This report uses a
home-build logarithm to generate projected future sales based on sales of the past
3 years. 3 year date period is always from current date. Report does not account
for seasonal sales, which may be very different.

**For the technically inclined, or if you just need to know, the
calculations for item Sales Trend Analysis report are as follows:**

**Average_Sales_Per_Month** = (3_Year_Sales / 36)

//~ Weight the sales periods differently, to obtain the ‘trend’

**Projected_Average_Sales_Per_Month** =
(
((3_Year_Sales – 1_Year_Sales) * 0.5) +
((1_Year_Sales – 6_Month_Sales) * 0.75) +
((6_Month_Sales – 3_Month_Sales) * 1.0) +
((3_Month_Sales – 1_Month_Sales) * 5.0) +
(1_Month_Sales * 12.0)
) / 36

//~ curve the results based on trend (this is just a linear increase/decrease, and is
minimized)
//~ this is the end result number for Projected Qty Needed, rounded to 4 decimal
places

_Chapter 14: Reports Zone_ **357** CA _User Manual_


**Project_Sales_For_Period** =
(Projected_Average_Sales_Per_Month * Report_Month) +
((Report_Month-1) * ((Projected_Average_Sales_Per_Month –
Average_Sales_Per_Month)/2)

**14.3.7 Sales Analysis Detail By Item**
The original report by this name was removed in version 2023.1 and replaced
by the report formerly labeled **SADBI Advanced**.

Clicking this button will open a **Report Prompts** dialog that allows you to
specify the Date Range plus quite a few other parameters.

Not having the **Show Transactions** checked will eliminate quite a bit of
information (detail) from the report.

Other parameters allow specifying a specific Customer, Customer Group, Price
Level, Item, Sales Rep or Inventory Group, and you can also Group the report
output by Inventory Group or Item Type.

The **Use Main Unit instead of Def. Selling** setting defines the way the
Totals for each Item are calculated. The report will convert each line items'

_Chapter 14: Reports Zone_ **358** CA _User Manual_


totals (not visible on report) to either the Default Selling unit (default) or the Main
Unit (if option checked).

The report shows a column for Measure Quantity (pg 243 ). Sales Analysis
Detail By Item: This report is quite powerful and often used. In this sample we
checked the options for **Group By Item Type** and **Show Transactions**.

_Chapter 14: Reports Zone_ **359** CA _User Manual_


**14.3.8 Customer Aging Summary**
The Customer Aging Summary report gives you a quick overview of Accounts
Receivable. This report has 1 parameter: Use Doc Date Instead of Due Date. If
this is checked then the report's age starts at date of document rather then date
Due. In that case the only sales marked as "Current" will be sales of the Report
Date.

**14.3.9 Back-Datable Aging Summary**
The "Back-Dateable" version of the Customer Aging Summary report has a
Date parameter that allows you to run the report showing data from a previous
date. **NOTE** : In databases with a lot of docs the standard (not Back-Datable)
version will load much faster.

**14.3.10 Customer Aging Detail**
This report provides more information, giving a breakdown of all Invoices each
Customer owes you. This view shows only a part of the report.

```
14.3.11 Customer Sales By Year
A "table" report that breaks down each customer's sales by Year. This report
```
_Chapter 14: Reports Zone_ **360** CA _User Manual_


is optimized for exporting to Excel sheet rather then Printing.

Note that this and all other reports, when saved as an Excel file the numbers
and dates come in as Text instead of Numbers, therefore can't be sorted properly.
Sorry, but this is a fault of the Jasper Reports software. We hope the developers
will eventually find a workaround for this.

For now, if you need true numbers try saving as a CSV file. This should open
with Calc / Excel, it has real Numbers and Dates, but does not contain any
formatting.

**14.3.12 Customer History**
Detailed history of customer's purchases and activities. Has numerous
parameters somewhat like Sales Analysis Detail By Item report, but is filtered per
Customer instead of per Item.

```
This report revised and expanded v2024.1
```
**14.3.13 Sales Per Hour**
Graphs showing Transaction Count and Sales Amounts broken down by Hour
of Day, Day of Week.

**14.3.14 Service Sales Graph**
Report that shows a Graph view plus Table of sales of Service Item s (pg 208 )
for a given date range. Has has numerous parameters to show either per Item or
per GL Account, and Qty Sold or Sales Dollars. This report is designed for
service-based businesses, to provide a quick overview of sales trends for a given
period.

**14.3.15 Customer List**
Simple list of Customer Name, Terms, Credit Limit and (optionally) Current
Balance.

**14.3.16 Customer Mailing List**
This report is is optimized for exporting a Customer list to an Excel file, with
various parameters for filtering and sorting.

This report includes columns for "Last Purchase" and "Total Purchases". Use
the date parameter to show only Customers that have made purchases since this
date. If the **Total Sales since Date only** option is checked then the Total
Purchases column will only show total of sales since the Date parameter,
otherwise it will show total sales for entire history of customer.

```
This report can help you determine who your active customers are.
```
**14.3.17 Customer Mailing Labels**
This report has the same parameters and data as Customer Mailing List, but is
formatted to print on standard 30-per-sheet address labels. Added v2023.1

_Chapter 14: Reports Zone_ **361** CA _User Manual_


**14.3.18 Customer Contact List**
List of Name, Address, Phone and Fax. Parameters for Customer Type and
Price Level. Has option to suppress the page Header and Footer to provide a
cleaner export to .xls report.

```
14.3.19 Customer Taxable Status
A report to show which Customers are set as Tax Exempt. Added v2023.1
```
**14.3.20 Customer By Gross Sales**
List of Customers and Gross Sales for a selected Report Period. Can set a
limit to show only if Gross Sales are equal or over a certain amount.

_Chapter 14: Reports Zone_ **362** CA _User Manual_


### 14.4 Expense And Payable.....................................................................................

Contains reports concerning your Vendor (Purchases) history and Accounts
Payable information. Reports are added and updated nearly every release.

**14.4.1 Open Document List**
Shows all Open documents of a specified type (Purchase Order / Vendor Bill,
etc). Can be limited to a single Vendor or Employee, and has options on how the
documents are sorted.

**14.4.2 Document List By Period**
A listing of Expense Documents for a selected period of time (date range).
Can choose which document type(s) to show. Can limit to a selected Vendor or
Employee if desired.

**14.4.3 Document Details By Period**
A more powerful report that shows not only the documents, but line items as
well (if **Show Doc Lines** is checked).

**14.4.4 Items on Open Purch. Orders**
A report to show what Items are currently on Open Purchase Orders. Has on
filtering by Item, Inventory Group, Vendor and Preferred Vendor. By default it
excludes items on Open (partially fulfilled) PO's that have already been Received,
but there is an option to include those lines.

**14.4.5 Repeating Quote Requests**
The Quote Request document (pg 238 ) has a Repeat Frequency option to use
for periodic reoccurring expenses. This report provides a list of all the
reoccurring Quote Requests, sorted by next due date.

_Chapter 14: Reports Zone_ **363** CA _User Manual_


**14.4.6 Purchase Analysis Detail By Item**
This is like the Sales Analysis Detail By Item report (pg. 358 ), except for
Purchases instead of Sales.

**14.4.7 Vendor Aging Summary**
A quick-glance report that shows how much money you owe your Vendors, and
how much is current or overdue.

**14.4.8 Back-Datable Aging Summary**
Like the Customer counterpart, there is a "Back-Dateable" version of the
Aging Summary report.

```
14.4.9 Vendor Aging Detail
Lists unpaid Vendor Bills.
```
```
14.4.10 Vendor Contact List
Listing of all Vendors with Phone / Fax / Contact.
```
**14.4.11 Vendor List**
Listing of all Vendors, option to show the Vendor's Balance (money you owe
them).

**14.4.12 Payments Made Per Vendor**
Report showing total dollar amount paid to a Vendor within a given Date
Range. Has options to hide details.

**14.4.13 Vendor By Gross Purchases**
Similar to Customer By Gross Sales report, shows total amount of purchases
made per Vendor in a given Date Range. This report breaks into multiple sections
for Vendor, Employee and Customer, as it is possible to write out checks
(expenses) to Customers as well as Vendors.

**14.4.14 Vendor History**
A purchase analysis report per Vendor. Has numerous options for showing /
hiding details and filtering per Document Type or Vendor.

**14.4.15 1099 Report**
This report contains the information needed to file your 1099 Tax forms. It
shows only Vendors and Employees that have **Eligible 1099** checked. This report
has a setting that allows generating a separate page(s) per Vendor / Employee,
with name, address and Tax ID showing.

_Chapter 14: Reports Zone_ **364** CA _User Manual_


**14.4.16 Sales Tax Liability**
This report shows how much Sales Tax you collected (owe) for the time period
specified.

When you click the **New Sales Tax Liability** button you will get a pop-up with
the following options:

- **Select Report Period** - Choose the time frame (month / quarter, etc) to
    get report on.
- **Cash Basis** - Report will be Accrual Basis if left un-checked. See Accrual
    vs. Cash Accounting, pg. 101.
- **Show State Totals** - If checked, this will give a per-state breakdown op
    sales.
- **Combine all Out-Of-State** - If check it will change the per-state
    breakdown to your state and all others combined, instead of all states
    individually.
- **Show Transaction Details** - If checked then the report will show all the
    transactions within the report period. Used for tracking down errors –
    Warning: this can give very long reports for larger businesses.

Note: A future update of CA may possibly revise the way Sales Taxes are
used / calculated to better support multiple taxes / tax regions and exemption
tracking.

_Chapter 14: Reports Zone_ **365** CA _User Manual_


### 14.5 Inventory Reports..........................................................................................

These reports are stock status lists and worksheets for Items, and Inventory
Items in particular.

Here is a brief description of each report and its usage.

```
14.5.1 Item List
A General purpose listing of all Items, or per filters.
```
**14.5.2 Item Stock Status**
Used to check the Qty On Hand of Inventory Items. Has columns for Qty on
Hand, Qty on SO, Qty on PO, Preferred Vendor and Order (needed).

**14.5.3 Inventory Worksheet**
Printout showing (supposed) Qty On Hand with fill-in blank to use for
Inventory check / Count. This report has parameter to hide / show Vendor Part
Number.

**14.5.4 Reorder Report**
This report shows quantities for Items that are on OPEN Sales Orders,
including components required for Manufacturing.

**14.5.5 Original Reorder Report**
Less detailed then the Item Stock Status report, just shows Inventory Items
that are at or below the Reorder Point.

_Chapter 14: Reports Zone_ **366** CA _User Manual_


**14.5.6 Item Transaction History**
Shows the entire transaction history of a single Item. Want to know why your
Qty On Hand in CA doesn't match your shelf count? Use this report to list all
Purchases, Sales and Adjustments of a selected Item.

**14.5.7 Item History By Date**
This is an extended version of the Item Transaction History report with a Date
Range filter and several Grouping and Filtering options. Shows multiple or all
Items and has a summary mode, which makes it much faster to get a quick
overview of Item usage for a given period compared to viewing the Item
Transaction History of each individual Item.

**14.5.8 Gross Profit Per Item**
Shows a summary of item Purchase Cost vs Sales Price for a given time
period.

**14.5.9 Invalid Inventory**
Used to check if each Item's Qty On Hand matches with the Sales / Purchases /
Adjustments that were made for it. If this shows any Items then you may want to
use the Reset Inventory Qty On Hand Utility to adjust the System's QOH (see pg.
135 )

**14.5.10 Calculated Inventory Value**
This is a fairly complex report that calculates the Value of all Inventory Items
by calculating the Qty On Hand and the Avg Value of the Items in stock based on
the (x) number of most recent purchases of that Item. Used for Inventory
Valuation, as the Inventory Asset GL Account is not dependable unless you set up
and use everything exactly right (even then it's questionable).

**14.5.11 Item Unit Analysis**
A fairly complex report that is designed to trouble-shoot your Unit setup in
Items. Has alert highlighting for Units that might have wrong pricing (not
consistent with main unit).

**14.5.12 Item GL Detail**
A report that shows the GL Accounts linked to each Item. Use to trouble-shoot
your system or confirm that all GL Account settings are correct.

**14.5.13 Item Price List**
There are 2 different formats of this report (1 column and 2 column) that can
be used as a customer hand-out price list. There is a little 'extra' feature in this
report – you can exclude desired Inventory Groups (pg. 130 ) from appearing in
this list by changing the Group's name to end with an empty space. The Inventory
Group selector on these reports support multiple selection (via. check-boxes) so

_Chapter 14: Reports Zone_ **367** CA _User Manual_


you can choose multiple inventory groups to print this way as well.

The Single-Column Price List has a parameter for displaying Item Name, and
also a parameter for optimizing export to Excel (excludes page Header and
Footer).

The **As Of Date** parameter prints on the sheet, which allows setting the
"Effective Date" of the price list to a future or past date.

Most of the Inventory Reports have parameters to limit results to a certain
Inventory Group or Preferred Vendor.

**14.5.14 Manufacturing Pick List**
This is the same Mfg Pick List (Manufacture document) described on page
228. It is for a particular Mfg Batch, it allows you to choose which Batch #
(Manufacture document) to print, as well as these additional parameters which
are not available through the Manufacturing screen (pg. 225 ):

- **Sort By** allow you to sort the printout by Bin Location rather then Item
    Number.
- **Hide Service Items (Labor)** suppresses all the Service type Items from
    the list.

**14.5.15 Manufacturing Per Item**
Same as the Pick List (previous), shows the Mfg Detail Per Item report (pg.
229 ) with additional options to control printout.

_Chapter 14: Reports Zone_ **368** CA _User Manual_


**14.5.16 Mfg Item Component List**
This is a report that allows you to view the Component List of a Manufactured
Inventory Item (pg. 202 ) rather then a Mfg doc. It includes Pricing and allows
selecting which Price Level to use. It also has an option to show the Components
Pricing as either the Cost or the Selling Price, with a total.

_Chapter 14: Reports Zone_ **369** CA _User Manual_


### 14.6 GL and Accountant Reports..........................................................................

These reports are Account reports used to determine details of GL
transactions, etc.

**14.6.1 Trial Balance**
Used to check current balance of all accounts, to see if the sum of all Credits
match the sum of all Debits. If Credits and Debits do not match then there is a
problem with the transactions recorded in Classic Accounting. In such a case, the
first step is to check the **Out of Balance Transactions** report, if unable to
determine and correct the problem you should contact your Classic dealer.

The Income, COGS and Expense Accounts (GL Account Numbers 4000 and
higher) will show only amount of transactions that occurred in the year of
selected report date. The Retained Earnings account – GL Number 3925 – shows
the total of all previous years earnings, same as on the Balance Sheet.

**14.6.2 Reconciliations**
Allows you to recall a previously completed Reconcile. See Reconciling your
Checking Account (pg 332 ).

**14.6.3 Deposits By Period**
A report that shows all the Deposits made in a specified time period for a
specified bank account. Has option to show all the payments on each Deposit.
Report added ??, manual updated v2023.1

**14.6.4 GL Account List**
A list of all GL Accounts. Shows GL #, Account Name and Account Type.
Account Type field is tagged with (Inactive) for inactive accounts.

**14.6.5 GL Detail By Account**
A report showing Detail OR Summary for One OR All GL Account(s). This
report includes a Summary option (don't check the 'Show Account Transactions'
option) and a running balance column (only if 'Show Account Transactions' is
checked).

**14.6.6 GL Entries By Transaction**
This is a 'system trouble-shooting' report that displays the GL Account entries
(Debits and Credits) that occurred for each Document. Has filters for Date Range
and Document Type.

_Chapter 14: Reports Zone_ **370** CA _User Manual_


**14.6.7 Check Disbursements by GL**
Select a single Bank account (pg. 94 ) and see where the money went. Breaks
down your checks by the GL Account that was used instead of by the Vendor. Has
an option to sort by Check Number instead of by Date (the default sort).

**14.6.8 Out of Balance Transactions**
This report shows transactions that are in error. If any transactions are shown
they should be checked out and attempted to fix. Often it is caused by an internal
calculation error and can be resolved by forcing the document to recalculate. You
can make the document recalculate by clicking on a couple of the Qty and Rate
cells in the Line Items grid, then Save the document.

If you have Out-of-Balance Transaction(s) that you can't resolve, you should
contact your Classic Dealer. Likely it is caused by an error in Classic Accounting.

_Chapter 14: Reports Zone_ **371** CA _User Manual_


### 14.7 My Reports....................................................................................................

If your Reports Zone is showing a My Reports tab, then those are reports that
were custom added using the Report Manager (see page 349 ).

### 14.8 Editing Reports.............................................................................................

Making and editing reports is pretty much for programmers and advanced
users, but here is some info in case you want to know.

**14.8.1 Jasper Reports and iReport**
All Classic Accounting reports and prints are generated by the Jasper Reports
library (a third-party software). These report templates are saved as plain text
files in an XML text format, with a file extension of **.jrxml** , but are normally
created using a graphical jasper report editing program.

There are 2 programs that can be used to create or edit jasper reports,
**iReport v5.6** (by Jaspersoft) or **Jaspersoft Studio** (by TIBCO, the current owner
of Jasper Reports). iReport is an older program that is no longer being updated
(5.6 is the last stable release), but the author prefers it over the newer JasperSoft
Studio. Both programs have some quirks of their own, so it's largely a matter of
what you're used to.

Both programs are available for download over the Internet at no cost. If you
use a CTS Steward or Choreboy processor contact your dealer for an update to
install iReport (a Jaspersoft Studio update is not available at this time).

It is also possible to do minor edits of a report using a plain text editor. Now
we do mean a **Plain Text** editor - never attempt to edit a jasper report using
**Writer** (OpenOffice / LibreOffice), Microsoft **Word** , or even **Word Pad**. On CTS
processors the **leafpad** text editor that is installed works fine. For Windows users
**Notepad** should do the trick. There are a lot Linux editors that will work fine,
like **Gedit** , **Geany** , **Kedit** , etc, and if you're really geeky you can use the likes of
**nano** , **vim** , and **emacs**.

**14.8.2 Getting a copy of a Standard Report**
If you want to modify and existing report or printout you need to first obtain a
copy of the correct .jrxml file.

These files are stored in a folder named **reports** that is inside the same folder
that the ClassicAcctApp.jar file is. If you can access this reports folder you can
just copy the appropriate file and you're good to go.

On CTS Steward / Choreboy word processors the reports folder is not
accessible, therefore we need to resort to other methods to get a copy of the file.

_Chapter 14: Reports Zone_ **372** CA _User Manual_


If we create a CA Backup that includes the Standard Reports we can extract the
report from there.

1. Check the **Include Standard Reports** option (see Backup Options, pg
    119 ).
2. Create a Backup (see Backup Database on pg 118 ).
3. Uncheck the **Include Standard Reports** option again (it takes up
    unnecessary space in the backup and on your file system).
4. Open the backup with xarchiver and Extract the desired report.

**14.8.3 Changing position of Check Signature**
A frequent complaint is that the signature does not print at the correct
location on the check (see Printing Signature on Checks on pg 325 ). This is due
to different printing companies placing the signature line at slightly different
locations (not all printers align exactly the same either). Here are step by step
instructions on how to modify a copy of the check printout (CheckVoucher.jrxml)
to adjust the signature position.

First you need to get a copy of the CheckVoucher.jrxml file to edit. If you
already have this, great! If not, see the previous section, Getting a copy of a
Standard Report.

Open the CheckVoucher.jrxml file in a text editor (usually double-clicking on
the file will do the right thing).

Search for the text _check_signature_. Usually hitting Ctrl+F on the keyboard
will open a Search Text dialog where you can type in the desired text, then click
the appropriate button to find it.

This should take you to a section of text that looks like the following (the text in
this document has some of the lines wrapped, it may display the line breaks
different on your screen).

<image hAlign="Center">
<reportElement x="378" y="174" width="202" height="48" uuid="983a50a9-
f416-4c2b-b814-d5b3e107cf26">
<printWhenExpression><![CDATA[new
File("reports_custom/check_signature.png").exists()]]></printWhenExpression>
</reportElement>
<imageExpression><![CDATA["reports_custom/check_signature.png"]]></
imageExpression>
</image>

The the searched text is highlighted in yellow, which is what the Search will
find for you.

_Chapter 14: Reports Zone_ **373** CA _User Manual_


The text we're actually interested in is highlighted in pink, this specifies the
position and size of the signature image.

- All the position and size numbers in Jasper Reports are 72 numbers per
    inch.
- **width** and **height** represent the size of the image.
- **x** is a distance from left in to the left edge of image.
- **y** is a distance from top down to the to edge of image.
- **x** and **y** values are relative to to the element's parent or band, therefore
    they are relative and not absolute (not measured from the edge of the
    paper).
Figure out about how much you want to move it, then calculate and adjust the
numbers from there. Say we decide that the signature needs to be moved upward
by ¼ inch.
1. Convert the amount to be moved to decimal inches: ¼" **(1 ÷ 4) = 0.25**.
2. Multiply the decimal value by 72: **0.25 x 72 =18** (this is the amount to
adjust - always round to the nearest whole number)
3. Since the y value is the distance from top down, and we want to move the
image up, we reduce the y value by 18. Using the value 174 in this
example, we end up with **156**.
4. So we change the text **y="174"** to read **y="156"** Be sure to retain the
quotation marks, and not change any spacing!
5. Save the file. Usually Ctrl+S will save.
6. Upload the modified CheckVoucher.jrxml file to the Standard Reports list of
the Report Manager (pg 349 ).
7. Test to see if it moved the correct amount. To test Check alignment reprint
an existing check onto plain white paper, then hold it against a check form
to see if it's aligned correctly (align the top edges of the papers). If not
correct, repeat.

_Chapter 14: Reports Zone_ **374** CA _User Manual_


### 14.9 Company Logo...............................................................................................

This section added v2023.1

If your company has a Logo you would like to have appear on your printed
documents you can do so. A logo consists of an appropriately sized PNG image
file and is added to CA via the Company Info dialog (pg 110 ).

The logo will appear in the top left corner of the document prints, replacing
the Company Name and Address that otherwise appears there. For this reason
the Logo image needs to include the Name and Address.

The area where the logo appears is sized to properly fit the top window of a
double window envelope. There is a slight difference in the size based on the Use
#9 Window Envelopes setting (pg 139 ).

- For #10 envelopes (setting not checked) size is: **3.415" wide x 0.75" tall**
- For #9 envelops (setting checked) size is: **3.2" wide x 0.9" tall**
    The developers have gotten complaints about the logo size, from users not
being able to display their logo properly. Hopefully someday CA will have a
feature that allows custom adjusting the logo size, but for now you will need to
have your documents customized if you need a different size.

**14.9.1 Create a Logo for Classic Accounting**
A basic tutorial to help you create or modify your own logo for optimal use in
Classic Accounting, written by Allen Hoover Jr.

This tutorial written for users of Classic Steward and Classic Choreboy word
processors.

Whether you create your own logo from scratch, or have a graphic designer
create a logo for you, these instructions will help you properly format your logo -
with return address included - for use in Classic Accounting(CA) documents.
These instructions assume you are using LibreOffice to do the final formatting,
and also assumes you have some knowledge in working with graphic entities and
text boxes in LibreOffice.

When you load a logo into CA for printing on documents, the logo replaces the
usual name/address field that prints on these documents. On income documents
such as Sales Orders, and Invoices, the logo prints in the return address spot that
lines up with the top window on a two window business document mailing
envelope. The name/address field - that prints unless a logo is loaded in CA – and
the logo fields were both designed to match up in size with the return address
window on a standard business document mailing envelope. This field is
approximately 3.75” wide by 1.25” high. When designing a logo, keep in mind it is
better to have the logo wider than tall, so it better matches the proportions of the

_Chapter 14: Reports Zone_ **375** CA _User Manual_


logo print field in CA documents.

If a graphic designer created your logo for you, have them send you the logo in
a PNG(Portable Network Graphics) file format. This is the best format for
working with the graphic in LibreOffice.

**1.** Start by opening a new LibreOffice
    drawing file. Go to Format > Page
    Properties, and set the Width (3.75”),
    Height (1.25”), and Margins (0.00”) as
    per this screenshot. Notice the Width
    and Height are set to match size of the
    Logo field in CA.

```
If you are creating your own logo from
scratch in LibreOffice Draw, you will
find it easier to use a full sized Draw
page to create and format the graphical
part of the logo.
```
**2.** Copy the logo graphic into the drawing file. Size the graphic to use as much
    of the page space as
    possible, while still allowing
    space to add a text box for
    typing your address.
    _Tip: Press F2 on the keyboard_
    _then use the mouse to draw a_
    _text box where you want to type_
    _your address_

```
The example to the right
shows a page that is ready
to do the final export to
PNG, to be imported into Classic Accounting.
```
**3.** Once the logo with return address is
    formatted and ready to be exported, go
    to File > Export. In the export screen,
    set the File Format to PNG – Portable
    Network Graphic (.png). Click on the
    Export button to bring up the PNG
    Options window in the next step.
    _Tip: If either a drawing/graphic entity, or a_
    _text box is selected in the drawing page at the_
    _time you click on File > Export, it will only_
    _export the selected entity to PNG, rather than the whole drawing page. This can cause_
    _unexpected results when exporting._

_Chapter 14: Reports Zone_ **376** CA _User Manual_


**4.** After clicking Export, the PNG
    Options screen appears as
    shown to the right. The default
    settings are low resolution,
    which can cause a logo to appear
    pixilated or blurry on a printed
    invoice. Changing the resolution
    to 300 or higher, will create a
    sharper looking logo. After
    changing the resolution, change
    the width back to 3.75”, and the
    height should adjust itself back
    to 1.25”.

```
Click Okay to save the logo to file.
```
**5.** Go to Classic Accounting,
    and open the Company
    menu, then click on
    Company Info, which brings
    up the screen shown on the
    right.
    Click the Browse button and select the PNG logo file you just exported. A
    preview of the logo appears to show how it will appear on documents.
    Below is a sample invoice with a logo printed on it.

_Chapter 14: Reports Zone_ **377** CA _User Manual_


## Chapter 15: How do I handle this?.........................................................

### 15.1 Sales Tax........................................................................................................

Sales Tax setup can be fairly simple or pretty complex, depending on your
State regulations.

#1. You can't operate CA without a Sales Tax Item (page 212 ). Even if you
never charge any sales tax, you still need to have a Sales Tax Item. There is a
setting for which Sales Tax Item is used by default when a new Invoice is created,
see Taxes tab (page 139 ) of Income Settings dialog.

```
A Sales Tax Item is the same thing as a Tax Region.
```
**15.1.1 If you never charge Sales Tax**
Create a Sales Tax Item with a Rate of 0.00. Set ALL **Customers** and **Items**
to be Exempt (See Customer Taxes Tab, page 269 and Item Taxes Tab, page 190 ),
so the Sales Tax doesn't show up as a line item on your Invoices. End of story.

**15.1.2 If you only have one Sales Tax**
Create a **Sales Tax Item** for the Tax with the proper Rate.
For each Item in CA that never gets charged Sales Tax, regardless who buys it,
set it to Exempt. Any Item that is possibly Taxable, don't set to Exempt.

For each Customer that is always Exempt from Sales Tax, set to Exempt. All
others, set to Taxable (no checkmarks in the Exempt column).

Check this Tax as the Default Tax Region in the Income Settings.
When creating Invoices or Sales Receipts, keep an eye on the Sales Tax line
that gets added. If the previously mentioned settings are done correctly, it should
be correct unless this sale is non-standard for some reason.

At the end of your reporting period, when you need to pay the Sales Tax that
you collected in the past period, view / print the **Sales Tax Liability** Report
(Reports Zone), being sure to set the Start and End dates correctly to cover the
time period that you are paying for.

Create a Vendor Bill to your Sales Tax Agency (Vendor), using an **Account
Items** entry of the amount of Sales Tax collected, to GL Account _2200 Sales Tax
Liability_.

Use Pay Bills (page 256 ) to create a **Bill Pay Check** to pay the Sales Tax.
Print (or write) the Check and mail it. If you **pay electronically** , don't actually
print the check, but enter a reference in the Check Number field such as _EFT_

_Chapter 15: How do I handle this?_ **378** CA _User Manual_


(Electronic Funds Transfer) or _TT_ (Telephone Transfer).

If your state offers a discount, you can accomplish this by means of a Terms
(page 111 ). Displayed here is a setup that generates the 0.75% Discount that is
allotted in the State of Ohio.

**15.1.3 Collecting multiple Sales Taxes**
Like previous, just a lot more of it. :(
Upon investigation this has turned out to be quite complex. Note that the
examples in this document are attempting to track different categories of Exempt
sales, not to track several different Taxes.

There are 3 factors involved here:

1. The Taxable / Exempt setting of the Item.
2. The Taxable / Exempt setting of the Customer.
3. The Taxable / Exempt setting of the Document.

Each Document (Invoice and Sales Receipt) must have at least one Tax Region
(Sales Tax Item) selected. CA will automatically select one or more.

When creating a Document, it will not set any Tax Regions until an Item is
entered. Then it does some fancy figuring:

For each Sales Tax Item, if either the Customer OR the Item is Exempt, it will
not use that Tax Item. Each Tax Item that is applicable will be set, and the Tax
Regions setting will be loaded with all of the Customer's Non-Exempt Tax
Regions, even if they're not used. If this result in no Sales Taxes being used, then
it will load the Customer's Non-Exempt Tax(es) as the default Tax Region for the
Document, but if the Customer has all Taxes checked as Exempt then it will load
the Tax Region(s) marked as Default Tax Regions in the Income Settings. If an
additional (exempt) Tax is checked to be used on a line item, then it will add that
Tax Region to the Document's setting when saved. OUCH! Headache Territory,
this is.

The unexpected issue the Author ran into was this: On the **Sales Tax
Liability** Report, the **Total Sales** figure for each Sales Tax Item is only the Total
of all documents where that Sales Tax Item is is checked in the document's Tax
Regions setting. In order to get an accurate Total Sales figure, it is necessary
that at least one particular Tax Region is ALWAYS checked on all documents.

CA will automatically check the Tax Regions for all the different Sales Taxes
that are used in that document, and it is possible to check additional Tax Regions
even if they're not used on that document. Meaning the Tax Region applies to

_Chapter 15: How do I handle this?_ **379** CA _User Manual_


that document, it just happens to be not used (exempt).

See Taxes Tab (page 210 ) of Service Item example and Discount Item example
(page 217 ) for more misleading information.

The Author thinks the samples given in this document of tracking multiple
categories are not correct, **_your corrections and suggestions requested_**.

_Chapter 15: How do I handle this?_ **380** CA _User Manual_


### 15.2 Credit Cards..................................................................................................

**15.2.1 Making Purchases**
If you use **Credit Cards** to pay Vendor Bills, it involves an extra layer of
transactions to keep all the GL Accounts correct. The CA entries required to
track Credit Card purchases reflect on the real-world transaction that are
involved - read the following carefully

You want to accomplish 2 things; first, keep track of how much money you owe
on the Credit Card, and second, have all the Credit Card purchases appear in the
correct COGS / Expense accounts.

1. Create a GL Account of Type **Credit Card** for each Credit Card account that
    you have. You also need a Vendor who you'll pay.
2. When you receive a Vendor Bill (or make a purchase) that you pay with a
    Credit Card, enter it in CA just like you would if you were paying with a
    Check, to the Vendor you purchased the stuff from. This creates entries in
    the proper COGS and Expense GL Accounts to show on your P&L Report.
    **Mistake #1 that is often made is not entering the Vendor Bill + Bill**
    **Pay (or Check) if it's paid by Credit Card**.
    A. If you entered it as a Vendor Bill (which you would do if you made a PO
       for the purchase) you will need to create a Payment for that Bill **using**
       **the Credit Card as the Paying Account**. Set the Payment Date for the
       date that you actually used the card to pay. This increases the Balance of
       you Credit Card GL Account. This payment is visible through the
       Checking section, but **you do not need to print it or assign a Check**
       **Number to it**.
    B.If you did not have a PO and made the entry as a Check, set the Bank
       Account to the Credit Card used to make the purchase, and set the
       Check Date to the date the purchase was made.
3. When you receive your Statement from the Credit Card company (bank),
    create a new Vendor Bill to the Credit Card Vendor. In the **Account Items**
    tab create an entry using the Credit Card GL Account, with the amount
    being the total of all new transactions this month - NOT INCLUDING
    INTEREST. This will reduce the balance of the Credit Card account, setting
    it back to 0.00 if you have not processed any Payments using this card since
    the Statement Date. This figure should be same as your Statement Balance
    unless you're carrying a balance from previous month(s), or occurred
    Interest / Penalty fees of some kind. **Mistake #2 that is made is to break**
    **this into the Expense accounts that the payments were for**. These
    entries are made already, in step 2.
    A. If you are paying the Statement Balance in Full immediately, you can skip
       the Vendor Bill entry and just create a Check using the same GL
       Accounts outlined above.

_Chapter 15: How do I handle this?_ **381** CA _User Manual_


```
B.Any Interest or Penalty fees will need to be entered as a separate line
using an Interest Payment Expense GL Account. This Interest entry will
show up as an Expense on your P&L. The entry to the Credit Card GL
Account will not show on the P&L.
```
4. If you created a Vendor Bill for the Statement, create a Payment (Bill Pay)
    for the CC Statement (Bill) using a Checking account to pay the bill. Print
    and Mail the check, or if you pay electronically and don't actually print the
    check, enter a reference in the Check Number field such as _EFT_ (Electronic
    Funds Transfer) or _TT_ (Telephone Transfer).
If you read through the Expense Zone chapter starting on page 231 you will
find some screen-shots and details of Credit Card payment entries.

**15.2.2 Reconciling your Credit Card Account**
Just like a Bank Account, you should Reconcile you Credit Card account(s).
This is like Reconciling a Bank Account, see Reconciling your Checking Account
on page 332.

**15.2.3 Accepting Payments**
This author has no experience in accepting Credit Card Payments. Perhaps
someone else can fill in the blanks here?

The Payment Type filter on Select Payments To Deposit dialog makes it easy to
separate the Credit Card payments received from other payments (Check, Cash,
etc.). See Deposit on page 326 for more information.

_Chapter 15: How do I handle this?_ **382** CA _User Manual_


### 15.3 Loans.............................................................................................................

For each Loan that you have, create one GL Account of type **Long Term
Liability**. A Line-of-Credit is same, except it should probably be a **Current
Liability**.

The balance of
this GL Account
should always be the
amount that you
currently owe on the
loan.

1. When you get
the initial Loan from
the bank, you'll need
to set the balance of
the Loan's GL
Account, as well as
get that same
amount into you
Checking account, or
what ever account that the loan was used for. To get money from the loan into
checking, make a **Transfer** (page 330 ) from the Loan account to _1090
Undeposited Funds_. Now the Loan Check will be available to **Deposit** (page 326 )
to your Checking account. If the Loan was deposited to your checking using an
Electronic Funds Transfer, you can make a Transfer From the Loan account
directly to your Checking account instead.

_Chapter 15: How do I handle this?_ **383** CA _User Manual_


If you're just starting with CA and need to get the balance correct on an
existing Loan, make a Transfer from the Loan account to _3000 Opening Balance
Equity_.

2. Each time you make a payment on the loan, create a Check (see Checking,
pg 321 ) to the holder of the Loan. Enter the amount you are paying on the
Principal of the Loan as an **Account Items** entry, using the Loan's GL Account.
This will reduce the amount (balance) of the Loan. You create a separate line
entry for the amount of Interest you are paying using a GL Expense Account
named Interest Expense. This shows as an Expense on your P&L Report.

**Print** the check to assign the proper Check Number to it.
Send the check to your lender! If you use hand-written checks, that's fine, but
you still need to do all these steps in CA in order 'balance the books' and to assign
a Number to the Check.

This section rewritten v2023.1. Previously it had been recommended to use
Vendor Bill + Bill Pay to make loan payments, but that requires an extra step and
does not add any benefit.

_Chapter 15: How do I handle this?_ **384** CA _User Manual_


### 15.4 Advance Payments / Account Credit.............................................................

Sometimes a Customer will make a Down Payment on some agreed-on service
or product, over-pays an Invoice, or wants to buy a Gift Certificate for later use.

CA has an **Account Credit** document for handling these situations. This
enables receiving a payment from a Customer without directly applying it to a
document.

This money received on an **Account Credit** becomes part of GL **2090 – Trust
Liabilities**. This is a Liability account rather then an Income account. The
Payment received will be available in Deposit (pg 326 ).

The Account Credit document shows up on the Receive Payment screen and is
used like a Credit Memo. When you apply an Account Credit toward an Invoice
the amount applied transfers out of Trust Liabilities and becomes part of your
income (Equity).

There is also an option for refunding the balance of an Account Credit to the
Customer, same as a Credit Memo.

**15.4.1 Receiving the Payment**

1. Open Receive Payment screen (see pg 289 ).
2. Select the Customer you received the payment from.
    ◦ If the desired Customer is not showing in the list because he/she has no
       OPEN Invoices, then un-check the **Show Only Customers w/Balance**
       option in order to select the correct Customer. The person needs to be
       entered as a Customer before receiving the payment.
3. Enter the payment information: Date Received, Payment Amount, Payment
    Method and Pmnt #
4. Click the **Save** button. You should get a message asking whether you want
    to retain the payment as Account Credit, something like shown in next
    image.
5. Click on **Yes** to confirm creation of Account Credit.
    ◦ If the Customer has OPEN Sales Orders or Invoices a dialog will appear
       with the OPEN documents listed (second image). _Checking one or more_
       _of the documents will create a link, or "tag", that indicates this payment_
       _is to be applied to that document later_.

**15.4.2 Over-payment**
In the event that a Customer over-pays invoice(s), intentionally or otherwise,
the process of receiving the payment is same as normal, except instead of
refusing to save because "Transaction is not in Balance" it will display the

_Chapter 15: How do I handle this?_ **385** CA _User Manual_


message asking whether you want to retain the over-payment as as an Account
Credit.

```
Gift Certificate
The Account Credit document should be usable for Gift Certificate purposes.
```
_Chapter 15: How do I handle this?_ **386** CA _User Manual_


**15.4.3 Account Credit view / edit**

Once you have created an Account Credit document you can view it from several
locations.

- On Income Zone screen right-click on the View/Edit button underneath
    Received Payments.
- In the Customer's Document History list.
- On a Sales Order or Invoice which has linked, or eligible to link, Account
    Credit there will be a green **Credit** label. Click on it to open a list of
    available Account Credit documents.
- On the Received Payment screen there is an Edit Credit button which will
    open the Account Credit that was created with this payment, or an Account
    Credit that is selected in the doc lines.

The "Editor" for Account Credit is a dialog rather then an in-application form
like Invoice, etc.

From this dialog you can:

- See information of the Customer, Payment, Linked documents and Used /
    Balance amounts.
- Link / un-link which document(s) the Account Credit is to be applied toward.
- View / Print a document with information about the Account Credit
- Create a **Refund** Check to return the unused amount to the Customer.
- View all the **Payment** that have been created with this Account Credit
    ◦ The Payments button has a drop-down option for **Open Original**
       **Payment**
- View all the **Links** for this Account Credit.

_Chapter 15: How do I handle this?_ **387** CA _User Manual_


Clicking on the Green **Credit** label on SO or Invoice form will open a dialog
that displays the available Account Credit documents. Double-clicking on a
document line will open the Editor dialog.

**15.4.4 Applying (using) the Account Credit**

CA has an alert feature to remind you of available credit.

When you save a newly created Invoice that has Account Credit available
(either linked to that SO / Invoice, OR Credit for that Customer that is not linked
to any specific document) a message box will appear, asking if you want to apply
credit.

If you click on the **Yes** button a dialog will appear that allows you to choose
which Account Credit(s) to apply.

When you click the **Apply** button the Receive Payment screen will open, with
the appropriate documents checked and amounts filled in for a $0.00 payment (no
money received at this time, only applying the Account Credit).

_Chapter 15: How do I handle this?_ **388** CA _User Manual_


In the view shown here there the total of the Credit ($500.00) is greater than
the total of the Invoice ($207.99), so only $207.99 of the Account Credit will be
used, and the Invoice will be paid in full.

There is a **Pay Method For Account Credit** setting in Income Settings, on
the Other Tab (pg 140 ). This allows you to preset a payment method to use when
applying Account Credit.

**15.4.5 Modifying and/or Deleting an Account Credit**
To modify the amount of the Account Credit, or delete it altogether, modify the
Received Payment where the Account Credit originates from.

You can find it in your view/edit Received Payments list, or open the Account
Credit editor dialog and right-click on the **Payments** button, then click on the
**Open Original Payment** option.

If you change the amount of the Received Payment and save, it will either
modify the amount of the Account Credit, or delete it if the payment amount is no
longer more than what is applied to Invoice(s).Deleting the Received Payment will
also delete the Account Credit.

The Received Payment cannot be modified or deleted if the Account Credit has
already been applied to Invoice(s), or if the Received Payment has been
Deposited.

_Chapter 15: How do I handle this?_ **389** CA _User Manual_


### 15.5 Advance Payment to Vendor..........................................................................

Method used by Countryside Plants, LLC. (added v2024.1)

We have an Item for Prepayment. When we need to prepay or make down
payments before we can receive the product, at the end of the PO needing
prepayment we enter the Prepayment item 2 times, both for the amount of the
prepayment. However, the first line has a qty of 1, next has a qty of -1.

Instead of receiving products so payment can be made, we only export the
prepayment item (qty 1) to a Vendor Bill and pay that. When we receive the
product, we also receive the negative (-1) prepayment line item. This offsets some
or all of the Vendor Bill amount due (by the amount of the prepayment).

This works very well for us and we don't need to try to remember that a down
payment was made.

**Editor Note:** GL Accounts were not specified, but the Purchases/COGS GL
should probably be an Asset account. It would probably be doable to use a similar
setup on the Income side for Down payments, in that case the Sales GL should be
a Liability account. (But Down Payments are a feature in CA, see Advance
Payments / Account Credit on pg 385 .)

### 15.6 Receiving a Vendor Credit Refund................................................................

If a Vendor sends you a Check (or other payment method) to cover a Vendor
Credit that is in your system, Classic Accounting can receive a Payment for this
that you can Deposit.

Simply go to the Pay Bills screen (pg 256 ) and Check-mark that Vendor Credit.
Click on Pay Bills button and it will ask if you received a Refund Check of this
amount. If you choose Yes then it will generate a Receive Payment that you can
deposit via the Deposit screen. If needed you can view or delete this document
through the Receive Payment section in the Income Zone.

_Chapter 15: How do I handle this?_ **390** CA _User Manual_


### 15.7 Returned Checks...........................................................................................

We're using some numbers in this section, to hopefully make it a little easier to
follow. We'll use nice even numbers to make it easier to calculate, which probably
won't be the case in real life.

Based on a situation that arose with the author's client the following might
provide you with enough information for you to come up with something that
works for you. If you have a better way to handle this please let the author or
CTS know.

**15.7.1 The Situation**

1. You receive check #1234 of $1,000 in payment for Invoice #567 from
    Customer Y.
2. You send the check to your Bank (Checking Account) with x number of other
    checks that comes to a total Deposit Amount of $5,000.
3. Some days later your Bank informs you that check #1234 of $1,000 was
    returned.
4. Now Customer Y owes you $1,000 again, plus per your store's policy he
    owes you an additional $35 for giving you a bad check.
5. You receive your (first) Bank Statement showing a Deposit of $5,000, plus a
    returned check, -$1,000.
6. Customer Y provides check #1238 of $1,035 to pay for Invoice #567 plus
    the $35 bad check fee.
7. You deposit the check along with some others for a total Deposit of $3035.
8. Everything clears and you receive a second Bank Statement showing the
    $3035 deposit.

**Method 1**
There is currently no “build-in” method in CA to handle returned checks. One
method, and likely the best one, is something like the following:

1. Delete the Deposit of $5,000 and re-create it without check #1234,
    changing the total to $4,000.
2. Delete the Payment #1234, which reopens the Invoice #567 as unpaid.
3. Create a new Invoice (#578) of $35.00 to Customer Y, amount owed for the
    bad check.
4. Reconcile the first Bank Statement. The $4,000 Deposit you show in CA is
    equal to the $5,000 deposit minus the $1,000 returned check, so the
    Reconcile balances.
5. Enter a Receive Payment for check #1238 to pay both Invoice #567
    ($1,000) and #578 ($35).
6. Reconcile the second Bank Statement. Everything matches, all OK.

_Chapter 15: How do I handle this?_ **391** CA _User Manual_


**Method 2**
For the client mentioned Method 1 simply does not work. The main reason
being that he uses Cash Registers in his retail store, and does not enter the
individual payments received in CA, just lump sums from the cash register prints.
So there was no actual Invoice #1234 and Payment for it in CA, therefore we
couldn't do the delete / redo steps.

We came up with the following, which has rather a lot drawbacks but was the
best I could come up with at the moment. Can you do better?

**_1._** We need a 'holding account' for the returned check, until we get a
    replacement. Create an Asset GL Account, **_1900 – Returned Checks
2._** Deduct the amount of $1,000 from checking because it is not there, make a
    Transfer of $1,000 From **_1010 – Checking_** To **_1900 – Returned Checks_**
3. Reconcile the first Bank Statement. Deposit of $5,000 matches and the
    Transfer of -$1,000 (on Credits tab) matches the returned check on
    statement.
**4.** Need to deposit the received payment of $1,035. Created a Transfer of
    $1,035 From **_1900 – Returned Checks_** To **1090 – Undeposited Funds**
5. Create a Deposit that contains the $1,035 Transfer plus an additional
    payment of $2,000.
6. Now we have an issue, GL account 1900 has a balance of -$35. This $35 is
    actually an Income that we collected for the hassle of dealing with the bad
    check. Fix this by creating a Journal Entry with a **Debit** of $35 to GL **_1900_**
    **_- Returned Checks_** and a **Credit** of $35 to **_4000 – Sales_**.
7. Everything matches up when we Reconcile the second Bank Statement.

Method 2 has a major weakness in that there is nowhere in CA that tells that
the check got returned **or** that the Customer owes any money. It does, however,
have a nice little account that tell you how much money you're currently out of by
your Customer's checks bouncing.

```
Method 1 also has its weak points:
```
1. The first Statement is not an exact match, you need to add 2 lines on the
    statement together to match one line in CA.
2. There is no evidence whatsoever that check #1234 ever existed.

```
Method 3
```
Harvey Shirk of AZS Brusher Equipment provided the following solution.

```
Setup:
```
- Create new GL Account: **_1900 Returned Checks_** _[Accounts Receivable]_

_Chapter 15: How do I handle this?_ **392** CA _User Manual_


- Create **Other Charge** Item " **_Returned Check_** " with Sales GL **1900** (new
    account)
- Create **Other Charge** Item " **_NSF Charge_** " with Sales GL **4000** (Income)
    **_Processing Returned Check:_**
1. Create a Journal Entry
    Credit to 1010 (or your Checking account), $1,000
    Debit to 1900 (Returned Checks), $1,000
2. Create an Invoice to Customer with bad check
    Use item Returned Check, rate of $1,000 (enter returned check info in
    Description)
       Use item NSF Charge, rate of $35
This appears to solve the problems pretty well, and should reconcile properly
if your bank shows the returned check as a separate debit on Bank Statement.
- The Journal Entry and Invoice will cancel each other out on the 1900
account.
- The Journal Entry will remove $1,000 from checking account.
- The Invoice will show $1,035 as receivable from customer.

If your bank shows the Deposit amount as $4,000 instead of creating an
additional entry for the returned check you can instead do the Journal Entry as
follows:

Debit to 1900 (Returned Checks), $1,000 (for bad check)
Credit to 1010 (checking account), $5,000 (deposit amount)
Debit to 1010 (Checking Account), $4,000 (deposit amount – returned
check)

Now reconcile (or Clear, via the Register) the bad Deposit ($5,000) and the
$5,000 credit Journal Entry from your Banking account, then the $4,000 debit
Journal Entry will match up with the Deposit listed on your Bank Statement when
you reconcile it.

_Chapter 15: How do I handle this?_ **393** CA _User Manual_


## Chapter 16: FAQS....................................................................................

### 16.1 Check Signature............................................................................................

**Q:** My signature prints on the line of the check, how can I correct this?

**A:** See Changing position of Check Signature on page 373.

### 16.2 Insufficient Permission.................................................................................

**Q:** Classic Accounting keeps telling me I need Admin permission, but I don't have
a password to get in. how do I get past this?

**A:** Select **Log In As...** from the **Company** menu (or use the Ctrl+L keyboard
shortcut), enter _admin_ (all lowercase, no spaces) for the User Name and leave the
password blank, then click the **Login** button.

The **Not Authorized** dialog contains a **Log In** button, clicking it (or hitting
the Space Bar when button is selected) opens the Log In dialog and continues the
action you started if you enter a valid User and Password.

### 16.3 Receive Payments Faster...............................................................................

**Q:** When a customer pays right away it takes too long to enter the payment after
creating the invoice, is there a faster way to do this?

**A:** After creating the Invoice, instead of just clicking on the **Save** or **Back** button,
click on the drop-down arrow on the **Save** button and select the **Save and
Receive** option. This will open the Receive Payment form (pg. 289 ) with the
correct Customer / Invoice(s) loaded.

The **Save** button on the Receive Payments form has a **Save and Print** drop-
down option, which allows you to print the Invoice(s) that were payed.

### 16.4 Wrong GL Account Used...............................................................................

**Q:** I selected the wrong GL Account when writing a Check but I cannot change it
because it has already been Reconciled (status is CLEARED). How can I fix this?

**A:** You can remove (or set) the Cleared status of transactions using the Register
in Banking Zone. See Changing Cleared Status on pg 319.

_Chapter 16: FAQS_ **394** CA _User Manual_


## Chapter 17: Troubleshooting..................................................................

**17.1.1 Problem: Display not readable**
When running Classic Accounting on Windows 10 computers with large high-
resolution monitors sometimes the controls on Classic Accounting screens are all
jumbled, shrunk, overlapping, etc.

**Solution** : Modify **compatibility settings** for the Java executable files.

1. Find your java installation, it should be in “ _C:\Program Files\Java\jre1.x...\_
    _bin_ ” (or in _Program Files (x86)_ if you installed a 32 bit version). It is
    possible you have multiple java versions installed, you can check the version
    being used by selecting Help > About... from the CA menu.
2. Right-click the **java.exe** file and select Properties.
3. Select the **Compatibility** tab
4. Check the **Overwrite high DPI ...** option
**5.** Set the **Scaling Behaivor** option to **System**
6. Click **Apply** then Close
7. Repeat steps 2-6 on the **javaw.exe** file. This is the program that should
    actually execute ClassicAcctApp.jar, if you use java.exe to execute it you'll
    get a Command window in the background.

```
17.1.2 Problem: Display hard to read, text is too small
Again an issue when using hi-resolution monitors.
```
**Solution:** There are settings for increasing the Font size, see Per Machine
Settings, page 114.

**17.1.3 Problem: Doesn't open, splash screen flashes then
disappears**
Since version 2022.1 Classic Accounting requires Java 8 to run. If you attempt
to launch CA using an older (less than 8) version of Java it will just briefly flash
the splash (startup) image on the screen then disappear.

**Solution:** Upgrade the java runtime (JRE) on your computer / word processor to
Java 8 (also known as Java 1.8).

_Chapter 17: Troubleshooting_ **395** CA _User Manual_


## Chapter 18: Appendix..............................................................................

### 18.1 The CA Dictionary.........................................................................................

If you are new to the world of Accounting and/or Computers you may
encounter words and phrases in this manual that you don't know the meaning of.
Here are some of them, with definitions.

```
 Non-Posting : A document or transaction that does not affect your financial
reports (P&L, Balance Sheet). Example: Sales Order, which is an order that
has been received, but is not considered Income because it has not been
fulfilled and/or invoiced yet.
 Unknown : Why there are no more entries here.
```
_Chapter 18: Appendix_ **396** CA _User Manual_


### 18.2 Keyboard Shortcuts.......................................................................................

For the "Power Users" out there, Classic Accounting has an impressive number
of keyboard shortcuts available.

```
18.2.1 General - throughout CA
➢ Ctrl+F = Find (opens the CA Search dialog, see pg 337 )
◦ If the focus is in a Table Control, or Data Table then Ctrl+F may open a
Find dialog for that table.
◦ This feature is build into the table control by default, some users like it,
but others consider it useless. There is an option in Menu > Company
Options > Per Machine Settings to enable / disable the search-in-table
feature. This setting is not implemented on quite all tables, some ignore
it. Setting added v2024.1.
➢ Ctrl+G = Go Back (on most forms triggers Go Back or Cancel).
➢ Ctrl+L = Log In (opens dialog for Logging In / Switching Users - pg 60 )
➢ Ctrl+Q = Quit (closes the Classic Accounting application)
➢ F1 = Help (opens this help document)
```
```
18.2.2 General - on Dialogs
➢ Ctrl+G = Go Back (often this triggers the Go Back or Cancel button).
◦ Beware that on most dialogs Go Back will close the dialog w/o saving!
➢ Esc = Cancel (usually closes the dialog w/o saving)
➢ Ctrl+Enter = Save & Exit (some dialogs will save & close with this
shortcut)
```
```
18.2.3 General - on Document Forms
➢ Ctrl+G = Go Back (on most forms this triggers Go Back or Cancel).
➢ Ctrl+O = Open (generally opens the Document Search Dialog - see pg 54 )
➢ Ctrl+P = Print (you can configure what happens with the Print Button
Settings dialog, see pg 47 )
➢ Ctrl+S = Save (saves the current document w/o clearing the form)
➢ Ctrl+0 (zero) = Show the Org Info Dialog (see pg 42 )
➢ F7 = Copy Doc
➢ F8 = Paste Doc
```
_Chapter 18: Appendix_ **397** CA _User Manual_


```
18.2.4 When focus in Text Fields
➢ Ctrl+A = Select All (selects all the text in the current text field)
➢ Ctrl+C = Copy (copies the currently selected text to the system clipboard)
➢ Ctrl+V = Paste (pastes the system clipboard contents at the current text
cursor location)
➢ Ctrl+X = Cut (like copy, but removes the text from current location)
➢ Ctrl+Enter =?
◦ On some fields (including in table cells) it opens the Multi-Line Text
Editor (pg 35 )
◦ In Calculator Cells (pg 38 ) it triggers the calculation
➢ F2 = On some fields (including some table cells) it opens the Multi-Line Text
Editor
➢ F6 = Opens the dialog for Inserting Special Characters (pg 57 )
```
```
18.2.5 On Invoice form
➢ F12 will trigger the Save & Receive action (pg 279 )
```
```
18.2.6 On Receive Payment form
➢ F11 will trigger the Save & Print action (pg 291 )
➢ F12 will trigger Save then Go Back action
```
```
18.2.7 On Sales Receipt form
➢ F12 will trigger the Tender button
```
```
18.2.8 On Sales Order form
➢ F12 will trigger a Save & Receive action to receive an Advance Payments /
Account Credit (pg 385 ) for the Customer (v2023.1).
```
```
18.2.9 On CA Search dialog
➢ F5 = reload the list
➢ Ctrl+R = reload the list
```
_Chapter 18: Appendix_ **398** CA _User Manual_


```
18.2.10 Navigating the Menu
See Menu Accelerators on pg 106
```
**18.2.11 Open specific document forms**
Many of the document forms and search dialogs have a specific keyboard
shortcut to open them. You can see what the shortcut is by looking at the Menu
option for the desired form.

As you can see on this screenshot, a New Estimate has a shortcut of Ctrl+E.
Throughout CA, if you hit Ctrl+E on
your keyboard it will usually attempt
to close the current form and open the
Estimate form with a new (blank)
Estimate loaded.

If you are on a document form with
unsaved changes it will ask if you
want to save your document before
closing.

Receive Payments shortcut was
changed to Ctrl+4 in version 2023.1.
Previously it was Ctrl+A, which
conflicts with the shortcut for Select
All (text).

_Chapter 18: Appendix_ **399** CA _User Manual_


## Alphabetical Index of Keywords...............................................................

#### 1

1099 Report................ **364
A**
Accelerators................ **106**
Account Credit. .142, 293,
**385**
Account Items............. 250
Account No...54, 127, **267**
Account Register......... 127
Account Type.........86, 127
Accounting.................... **85**
Accounts Payable..22, **86,**
103
Accounts Receivable...22,
**86,** 103
Accrual vs. Cash......... **101**
Acknowledgments........... 4
Activate......................... 53
Active check box........... **44**
Add................................ 17
Add Job........................ 340
Add or remove custom
reports........................... 47
ADD TAX...................... 278
Adding New Customer 137
Adjustment Account.... 131
Admin Tasks................ **117**
Advance Payments...... 385
Advanced Options......... 17
Alert Notes..........235, 268
Alert Notes label........... 31
Also Print....................... 48
Always Show on Startup
...................................... **17**
Annual Interest Rate... 301
Application.................... 11
Applied / Owed............ 278
Apply To All................. 216
Apply To:..................... **216**
Apply Update............... 108
Assess Finance Charges
.................................... **302**
Asset........................86, 96
Asset account...... **91,** 195,
218

```
Asset Count................. 218
Asset Item................... 218
Assets............................ 86
Attach a note............... 243
Attachment Name....... 345
Attachments................ 344
Auto-Load Item Manager
.................................... 134
Average Cost............... 189
B
Backup Database........ 118
BACKUP IS IMPORTANT!
.................................... 118
Backup Options........... 119
Balance Forward......... 306
Balance Sheet............. 220
Banking....................... 317
Banking Menu............ 148
Banking Settings........ 148
Barcode Scanning....... 297
Base Price...178, 252, 281
Batch Printing............... 48
Bill Pay Check...104, 257,
325
Bug................46, 183, 230
Build............................ 227
Button............................ 26
C
CA................................. 11
CA Report Manager.... 150
Cached........................ 150
Calculate Charges From
.................................... 302
Calculated Inventory
Value............................ 367
Calculator Cells............ 38
Cards.......................... 267
Cards Button............... 268
Cash.............................. 94
Cash Basis.................. 101
Cash Customer............ 267
Cash Register................ 94
Change To Inventory... 188
Check.......................... 104
Check Disbursements by
```
#### GL................................ 371

```
Checking.............. 94, 321
Choose Database........ 125
Choose Database
Connection.................... 15
Clear All Preferences.. 117
Clear Print Button
Settings....................... 150
Clear Report Cache.... 150
CLEARED......33, 319, 335
Click.............................. 26
Close Old Estimates.... 144
CLOSED........................ 33
Code............................ 212
COGS............................. 92
COGS vs. Expense........ 92
Column Control............. 35
Column Widget............. 36
Column Width............... 35
Combo Box.................... 29
Company Info............. 110
Company Logo............ 375
Company Menu........... 110
Company Name........... 264
Company Options....... 111
Compatibility settings. 395
Components......134, 204,
206, 207
Conservative Technology
Services, Inc.................... 4
Converting Documents 286
Converting Non-Inventory
to Inventory................ 192
Copy Count.................... 46
Copy Doc..................... 338
Copyright........................ 4
Cost............................. 178
Cost of Goods Sold...... 354
Create Bill...........241, 247
Create Customer......... 233
Create Invoice............. 270
Create Payment........... 254
Create Template............ 71
Create Vendor............. 270
Created / Modified Label
```
_Alphabetical Index of Keywords_ **400** CA _User Manual_


#### ...................................... 32

Created date.................. 32
Creating new Sales Order
.................................... 138
Creating Purchase Orders
.................................... 286
Credit Card........... **95,** 267
Credit Cards............... **381**
Credit Limit.........234, 267
Credit Memo............... **287**
Ctrl+F.....................4, 337
Ctrl+G.....................25, 42
Ctrl+P........................... 40
Ctrl+R......................... 337
Ctrl+S......................... 108
CTS.................................. 4
Current Asset.............. 127
Current Value.............. 219
Cust. Msgs.................. **143**
Customer Criteria....... 272
Customer Signature.... 138
Customers................... **263
D**
Data Table..................... **34**
Database....................... **14**
Database Bin Path....... 120
Database Utilities....... **117**
Date Based.................. 112
Date Control.................. 31
Default......................... 218
Default Discount GL..142,
**146**
Default Exempt........... 213
Default Formula.......... 154
Default GL Accounts..... 99
Default Payment Account
............................146, **148**
Default Rep................. 266
Default Rounding........ 154
Default Ship Via. .137, 145
Default ShipAddr........ **265**
Default Terms......145, 266
Default Type................ 145
Delete.......................... 271
Delete GL Account...... **126**
Deleting Documents /
Transactions................. **41**
Deposit................103, **326**

```
Deposits By Period...... 370
Depreciation............... 220
Description.................. 280
Dialog............................ 27
Disable Country Fill.... 116
Discard.......................... 45
Disclaimer....................... 4
Discount...................... 290
Discount Date.............. 111
Discount Item.............. 214
Display not readable... 395
Doc Status................... 236
Document.................... 231
Document History....... 236
Document Number....... 30
Document Status........... 33
Document Type........... 236
Double-Entry Accounting
.................................... 105
Down Payment............ 293
Drop Ship.................... 141
Drop-down.............29, 241
Drop-Down Buttons...... 38
Due Date..................... 111
Duplicate..................... 229
E
Edit Button Settings41, 47
Edit GL Account.......... 126
EIN.............................. 235
Employees.................. 316
Enable Inventory Items
............................ 133, 191
Entry.............................. 88
Equity............................ 86
Equity Accounts............ 91
Estimate...................... 274
Expense......................... 92
Expense Menu............ 145
Expense Settings........ 145
Export Item List.......... 121
Extras.................183, 197
Extras Tab................... 182
F
F.O.B........................... 242
F2................................ 164
F5................................ 337
File Menu.................... 108
Filter......................52, 236
```
```
Finance Charge.. 137, 301
Finance Charge Item...22,
302
Finance Charge Settings
.................................... 301
Financial Reports....... 101
Fixed............................ 215
Fixed Date.................. 112
Font............................. 352
Font Extensions........... 352
Font Size..................... 115
Form Stacking............... 58
Forms..................... 27, 29
Formula....................... 199
Fulfilled......................... 33
G
General Ledger Menu. 126
Geographic Area......... 212
Gift Certificate............ 386
GL Account List........... 370
GL Account Number...... 86
GL Account Types......... 91
GL Accounts......... 86, 126
GL Detail By Account.. 370
Global Settings........... 116
Go Back......................... 25
Grace Period................ 301
Gross Profit................. 354
Groups......................... 236
GUI................................ 13
H
Help Menu.................. 151
History Tab................. 186
Home............................. 24
Horizontal Scroll........... 36
Host............................... 15
I
ID Number.................. 234
If Discounted:............. 216
Import / Export Items. 121
Import / Export Names
.................................... 124
Import Doc Items.......... 81
Import Item List.......... 122
Important.................... 250
Importing.................... 286
Importing Items.......... 286
Importing New Items.... 68
```
_Alphabetical Index of Keywords_ **401** CA _User Manual_


In-Table Search........... 115
Inactivate...................... 53
Inactive Customers..... 263
Income Accounts........... 92
Income Menu.............. **137**
Income Settings.......... **137**
Incorrect inventory count
.................................... 192
Initial Setup................... 22
Insufficient QOH Alert 142
Interest Fee................. 211
Invalid Inventory......... 367
Inventory..................... 195
Inventory Adjustment.. 132
Inventory Adjustments
.................................... **131**
Inventory Group..188, 216
Inventory Groups........ **130**
Inventory Item.....134, 191
Inventory Items.......... **191**
Inventory Method....... **133**
Inventory Reports....... **366**
Inventory Tab.............. **133**
Inventory Variance....180,
190, **195,** 354
Inventory Worksheet... 366
Invoice................103, **277**
Invoice Preferences..... 137
IP Address..................... 16
IReport v5.6................ 372
Is Current Asset.......... **127**
Item............................. 279
Item #......................... 280
Item Bulk Edit............. **222**
Item Combo Box. **34,** 187,
188
Item Components........ 204
Item Components Needed
.................................... 227
Item Cost..................... 178
Item Description......... 204
Item GL Detail............. 367
Item List...................... 366
Item Manager.............. 130
Item Name..........124, 188
Item Number............... 187
Item Price List............. 367
Item Quick Edit........... **130**

```
Item Receipt............... 246
Item Restock List........ 249
Item Settings.............. 132
Item Stock Status........ 366
Item Stock Status Report
.................................... 196
Item Transaction History
.................................... 367
Item Types................... 168
Item Unit Analysis....... 367
Item Utilities............... 135
Item Widget................... 34
Items........................... 167
Items Menu................. 130
Items To Build............. 226
J
Jasper Reports.....349, 352
Jaspersoft Studio......... 372
Job............................... 132
Job Column................. 340
Jobs.............................. 116
Jobs Tab....................... 270
Journal Entries............ 128
Journal Entry.......129, 219
K
Key................................. 45
Keyboard Shortcuts.....43,
397
Keys............................. 106
L
Label Printing................ 51
Labor........................... 204
Laser Checks............... 323
Last Modified date........ 32
Liability......................... 86
Liability Accounts......... 91
Limit To Vendor........... 256
Line Items................... 250
Line Links..............38, 253
Links............................ 387
Loan........................ 96, 98
Loans.......................... 383
Location...............196, 280
Lock Printed Invoices.. 138
Log.............................. 151
Log In.......................... 125
Log Level.................... 151
Log Off To Guest........... 62
```
```
Log-In Dialog................. 60
Logoff............................ 62
Long Term Liability....... 96
Look & Feel................... 17
M
Main Unit.................... 156
Manufacture Detail
Report......................... 227
Manufacture Details.... 226
Manufactured.............. 204
Manufacturing............ 225
Manufacturing Per Item
.................................... 368
Manufacturing Pick List
.................................... 368
Margin........................ 153
Mark Printed................. 47
Markup....................... 153
Markup %.................... 252
Markup Formula.178, 209
Markup Formulas....... 162
Math Operations
(scanning).................... 298
Meas. Qty..................... 280
Memo..................244, 330
Menu Accelerators...... 106
Menu Bar........24, 25, 106
Menu Shortcuts........... 106
Merge.......................... 271
Mfg Cost based on
Components................ 134
Mfg Item Component List
.................................... 369
Mfg Pick List............... 228
Minimum Finance Charge
.................................... 301
Multi-Line Text Editor... 35
Multi-Selection.............. 57
Multi-User..................... 14
Multiple GUIs................ 13
Multiple-user................. 30
My Reports.................. 349
N
Name Box...................... 29
Name Extension.232, 263
Name field................... 264
Negative Accounts...... 105
Negative Balance
```
_Alphabetical Index of Keywords_ **402** CA _User Manual_


accounts........................ 89
Negative Number........ 287
Net Income.................. 354
New............................... 26
New Credit.................... 27
No Charge Sales......... 267
Non-Inventory Item..... 187
Non-Posting..........76, **396**
Non-Posting Transactions
.................................... 104
Not Authorized.............. 62
Note.....................265, 278
Notes...................235, 282
Notes (Document)....... 244
Notes (Line Item)........ 243
Notes field..................... **37**
Notice.......................... 309
**O**
On S.O. Filter................ **82**
OPEN......................33, **41**
Opening Balance...98, 131
Org................................ 28
Org Groups................. **342**
Other Charge Item..... **211**
Other Income................ **92**
Other Tab....134, **184,** 197
Out of Balance
Transactions................ 371
Over-payment.............. 385
**P**
P.O./Rec. #................... 252
P&L Report................. 167
Pack All Columns........... 36
Pack Selected Columns. 36
Packing List................. 286
PAID............................... 33
Pay Bills..............104, **256**
Pay electronically........ 378
Pay Method.........142, 330
Pay Method filter......... 327
Pay Periods................. **314**
Payment Methods....... **113**
Payments..................... 253
Payments (button)....... 279
Payroll Items............... **315**
Payroll Menu............... **149**
PCI Security Standards
Council........................ 267

#### PDF................................ 50

```
PDF <doc type>............ 40
PDF Printer................... 50
Per Machine Settings. 114
Percent........................ 215
Percent Discount
Functionality............... 216
Petty Cash..................... 94
Point-Of-Sale.....139, 262,
294
Port................................ 17
PostgreSQL................... 14
Posting........................... 76
Preferred Vendor........ 189
Prev / Next.................. 175
Price increase.............. 209
Price Level............32, 267
Price Levels..... 130, 154,
179, 209
Price Rounding Mode. 134
Price-In-Barcode patterns
.................................... 298
Print...................... 45, 330
Print Action........... 47, 115
Print Button.................. 40
Print Preview................ 49
Printed........................... 33
Printing................. 46, 138
Printing Checks.. 317, 324
Printing Signature on
Checks........................ 325
Printout Customization
.................................... 185
Profile............................ 19
Profit & Loss Report.... 208
Projects....................... 116
Prompt Payment Discount
.................................... 111
Purchase Description. 188
Purchase Order........... 240
Purchase Tab.............. 179
Purchase/COGS Account
.................................... 189
Q
QOH....................191, 280
Qty............................... 281
Qty On......................... 135
Qty on Hand........132, 191
```
```
Qty On SO................... 275
Quote Request............ 238
R
Rate............................. 281
Rate Type.................... 215
Rates........................... 208
Recalc Avg Cost & Pricing
.................................... 135
Recalc Qty On PO & SO
.................................... 135
Recalculate All............ 127
Receive Payment103, 289
Reconciliation............. 129
Reconciliation Date..... 333
Recordkeeping.............. 85
Refund.................288, 387
Refunding.................... 385
Refunds...............104, 292
Register...................... 318
REM TAX..................... 279
Reorder Report...196, 366
Report Manager. 150, 349
Report Prompts........... 358
Reports............... 348, 349
Reports Menu............. 150
Reset Inventory Q....... 135
Reset Tax Migration.... 124
Reset Transactions..... 119
Resolve Conflicts........... 81
Restore Data............... 119
Returned Checks........ 391
Rod and Staff................. 85
Round To.............165, 179
Rounding errors.......... 281
Rounding Mode.......... 165
Rounding with Formulas
.................................... 165
Row Controls................. 37
Row Sorting.................. 36
S
S.O. / Est...................... 282
SADBI Advanced......... 358
Sales Account.............. 178
Sales Analysis Detail by
Item............................. 167
Sales Description........ 177
Sales Discount............ 214
Sales Order................. 275
```
_Alphabetical Index of Keywords_ **403** CA _User Manual_


Sales Receipt......139, **294**
Sales Rep....................... 32
Sales Reps.................. **113**
Sales Tab..................... **177**
Sales Tax.....91, 135, 136,
183, 212, 217, 348, **378**
Sales Tax Item.....30, 139,
**212**
Sales Tax Liability....... 365
Sample of PO printout **245**
Save & Print................ 291
Save & Receive...276, 279
Save As........................ 172
Save Button................... **41**
Save Changes?.............. 43
Save to File................. 123
Save Trans Search
Columns...................... 115
Saving Documents........ **45**
Search Dialogs.............. **52**
Search For..................... 52
Searching...................... 52
Security......................... **59**
Security Zones........59, 61
Select Payments for Date
.................................... 327
Selling Price....... **178,** 209
Server............................ 14
Service Item................ **208**
Ship To.......................... **31**
Shipping Address........ **265**
Shortcut...................... 106
Show Customers......... 322
Show Dual Search....... 115
Show Inactive Items.... 173
Show Items On Order
alert............................. 146
Show Log.................... **151**
Sorting......................... 236
Special Characters........ 57
SQL Query Tool........... **124**
SSN............................. 235
Standard Reports........ 349
Statement........... **305,** 332
Statements.................. **305**
Status..................240, 275
Status Fields................. 32

```
Status Indicator........... 278
Storewide Discount.... 142
Sub Account................ 127
System........................... 11
T
Table Control................ 34
Table Row Sorting......... 36
Tax Agency.................. 212
Tax Exemption............ 213
Tax Exemption Info..... 269
Tax Liability Account... 212
Tax Rate...................... 212
Tax Region............ 30, 212
Tax-Exempt.................. 183
Taxes........................... 282
Taxes Tab.................... 183
Tender................ 295, 398
Terms..32, 111, 234, 251,
266
Thermal Roll printer... 294
Timecards................... 312
Title for Estimate Printout
.................................... 139
To Invoice................... 295
Total............................ 282
Total Wt....................... 185
Transaction................... 88
Transaction Linked....... 33
Transaction Years....... 116
Transactions............... 103
Transfer...................... 330
Trial Balance............... 370
Troubleshooting.......... 395
True Type Font............ 352
U
Undeposited Funds..... 103
Unit............................. 280
Unit Name................... 156
Unit Of Measure.......... 181
Unit Of Measure.......... 181
Units 156, 190, 208, 209,
213
Units Tab.................... 181
Unknown..................... 396
UPC............................. 200
Update........................... 11
```
```
Update Cost from
Purchases................... 190
Update Item Cost........ 131
Update Item Sales Tax 135
Update Taxes............... 183
Updating Items.............. 69
Use Short FC Description
.................................... 302
User............................... 25
User Interface............... 13
Users.....................59, 125
V
Variance...................... 354
Vendor Bill..........103, 250
Vendor Credit Refund. 390
Vendor Note................ 238
Vendor Terms.............. 251
Vendor's Part Number 189
Vendors....................... 232
Version Updates............ 21
Via Methods................ 113
View Inv....................... 291
W
Warning....49-51, 66, 112,
113, 119, 120, 123, 135,
139, 151, 182, 183, 192,
199, 204, 217, 221, 230,
233, 256, 259, 264, 265,
270, 277
Warning:...................... 267
Watermark.................. 282
Weight......................... 185
Windows........................ 16
X
X.................................. 108
Z
Zip Code..............233, 265
Zone.............................. 24
Zones............................ 26
............................... 40, 41
See Units on page 156 for
more details on using
Units............................ 181
```
```
.................................... 286
%
% of Total Income........ 354
```
_Alphabetical Index of Keywords_ **404** CA _User Manual_


