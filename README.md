# Notion-Automations
This repository was created to enable automation using python with the notion API

I first started thinking about this project when I learned I can use the notion API in order to interact with my databases using the IOS shortcuts app

Later I wanted to make it more useful for myself.
The database I am using the automation for is a financial tracker.I have an automation on my iPhone that I menually enter the amount of money I spent and choose the ctegory and sub-category.
using the notionAPI the IOS shortcut sends it to the notion database I created and creates a new page with the information I provided. (amount, category and sub-category)

Further down the line I wanted to have get an update on the weekly status of my spendings, in other words I wanted to see how much I spent on each category without having to go inside the notion app on my phone and searching it myself.

And THAT is when I started working on this project

DISCLAIMER
This is my first time ever trying to interact with an API

The first struggle was when I discovered notion doesn't have native webhooks (first time I learned about webhooks as well)

but then I saw notion has an automation with Slack! so I started reading about the Slack API and used it as my trigger in this automation.

THE AUTOMATION'S PROCESS
When a page is created inside my notion database, using a notion automation, a message is sent inside a Slack channel that I've created for this automation.
The message that is sent inside the Slack channel is triggering a function that is calculating how much I've spent so fat this week on each category.
Using an SMS service API an SMS is sent to my phone letting me know how much I've spent on each category so far this week.


AND THAT'S IT

This took 2 full days of researching and discovering how to do everything

I used 'ngrok' for the request URL that the Slack API will send notifications to and once I saw the automation fully worked on my local machine I uploaded everything to GitHub


23.2.24 UPDATE

I've decided to have this automation run at all times so I used Render.com in order to have my Flask app running on a web server 24/7.
So I ditched 'ngrok' and used the provided request URL that Render.com has provided me.
This project is now up and running on a web server at all times letting me know how much I have spent on each category each time I create a new page on the notion database.
HOW EXCITING!
 
