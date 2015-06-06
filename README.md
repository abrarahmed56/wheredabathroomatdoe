# wheredabathroomatdoe
A crowd-sourced public utility rating and locator application for when you need a bathroom, bench, water fountain, etc.

## Style Guide
https://www.python.org/dev/peps/pep-0008/

## Schedule
- By May 8th, complete basic website framework including the login system and user interaction system.
- By May 15th, complete writing an API and integrating other APIs we may be using (Google Maps)
- Afterwards, improve UI and usability on website, and make optimizations/cleanup.

## Members
**Abrar Ahmed**  
**Aaron Mortenson**  
**Chesley Tan**  
**Eric Kolbusz**  

## Organization of The Website
- Home page will have a link to login if you are not logged in
- If you are logged in, show personal locations/favorites
- Have a link from the homepage (whether logged in or not) to browse popular locations
- The search bar will be at the top of each page
- After searching, a list of locations will appear
  - Under each location, show the average rating, and a few of the most recent reviews
- There will be a page for each location showing all the reviews, as well as pictures
  - Also, show suggestions for other locations nearby

## Database Schema
### User database
- Unique User ID -> String/ID
- Email -> String
- Email confirmed -> Boolean
- Password -> String
- Phone number -> String

### Game database
- Unique User ID -> String/ID
- Points
  - Caching layer to generate the rankings scoreboard
- List of listings with their associated lister rating -> [(Listing, Lister rating)]

### Listing database
- Unique User ID of lister -> String/ID
- Location -> (???)
- Reviews -> [String]
- Rating -> Integer
- Last updated date -> Date

## Set up dependencies
See `dependencies.md`  

## To-do List
- Set up email for website
- Email reset password feature
- Post utility review feature
- Update utility review feature
- Delete utility review feature
- Upload utility picture
- Report utility feature
- Favorite utility feature
- Upload user profile picture
- Report user feature
- Disable account feature (report threshold)
- User ranking feature
- Sms confirmation
- User search feature
