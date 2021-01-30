# My Notes

This was my submission for the Citi HBCU Hackathon in 2021. The project although slightly functional, is incomplete. I am not too sure on proper organization/naming of files, so the file titled CropPlusDetect.py is the file to run and the output will be shown on recognition.csv. Data.csv is the list of correct answers for the original data set.

I do think this project has lots of potential given the impefectedness of my algorithms and the lack of machine learning being throroughly intergrated. To get a better understanding, the following is the process that is used to take a picture of a check and produce the analysis. The individual files for each will (soon) be present in the "Puzzle Pieces" folder:

-East_Text_Detection: This was the original, pre-trained ML algorithm used to highlight where words may be on a picture
    
-OpenCV2's crop: An example found that was able to create temporary images that are selected portions of an original based on where the user clicks and highlights. This was modified by me in order to look at areas of a check as opposed to user input

-Google's Tesseract: This software was able to output what the computer read on the images and allowed me to store that value into something manipulatable.

-Word Assumption: Given that part of the task was to look at the check amount in word form, I knew what words to be expecting (e.g. "one - ten", "twenty, thirty,...ninety", "hundred, thousand, million..." etc.) Using this, the Word Assumption algorithm attempts to *assume* what word the Text Detection thinks it sees in order to remove the erros produced by varience in human handwritting. For example, if the TD reads the word "ane", the word "one" would get the highest score for being the closest word to it in terms of word length, number of letters shared, segments of the read-word in the assumed-word, and the word that came before it. It also included a way to reevaluate a previous word if it cannot find an appropriate successor (Ex: Assumed word 1 to be "four" but the next word does not match with hundred, thousand, million, etc., so the first word is reevaluated at "forty" and now our current word matches with "six". "Forty Six" makes sense but "Four Six" does not).
(However, there is one issue I seem to have forgotten in my algorithm somehow, which is numbers 11-19 XD. I don't know how I looked at so many checks and recited numbers so many times in my head and still forgot to include these in the algorithm. This is why I needed a team lol)

-Number Assumption: Similar to the Word Assumption, the Number Assumption attempts to correct errors in the Date and Dollar Amount listed on the check. TD reading "BI.00" might be read as "31.00", in order words turning letters into their most likely numerical counterparts based on many of the errors I was seeing. It is less effective than the Word Assumption due to the lack of patterns in number order, but still helps. This was inspired by this study: https://www.ismp.org/resources/misidentification-alphanumeric-symbols
    
Machine Learning is "already present" in the East_Text_Detection as it is a trained model for a different dataset. I wish I knew how to interact and understand the algorithm so I could know how to train it to the desired set. I think it could also easily be applied to both of the Assumption algorithms as well. Using a learning process to reevaluate the weights of each of the segments of the Word Assumption (length, segments, letters shared) would be helpful as I noticed the correct assumptions being close to the score threshold but being held back because these three segments have unchanging weights.

I also wanted to have an "assumption comparison" in order to compare the dollar amount in words and in numbers to see which is more correct and how much they match in order to make the outputs match. Both time contraints and lack of access to the original TD system made this out of reach.

As for full business implementation, the similar process could be used to help prevent obvious fraudulent checks by checking the length of the routing number, a matching check number, correct bank names, etc. 

Lastly, below were the original instrucitons for the Hackathon. Feel free to download the dataset, then go into the CropPlusDetect file and set the Path to where you save the folder. The program will attempt to run through all the checks in the folder and display the output before soon crashing :/. Lol thanks for checking out my solution!

----------------------------------------

# Context

Artificial intelligence is everywhere around us and is growing more and more prevalent each day. One area that AI has recently gained traction in is the automation space. Why have a person read a long and complex legal document when a machine can do it faster and more accurately? But what about when things get messy; like (some people's) handwriting. People are pretty good at reading handwriting of various quality, but how good are machines at it? Lets find out. Now as a bank, we thought about where we most often see handwriting nowadays. Thankfully, most transactions have been digitized. Except for one place: Checks.

As far as technology limitations go there are none. Just make sure your solution is able to be packaged in a way where we can take a look at it.

# Content

The data for this competition is organized as follows:

- data.csv
    - A comma separated value file laid out with headers indicating, in order, the path to the image from this directory, the date as written in the check, the check amount as written in words, and the check amount written in numbers. The path is relative to this directory. The order of images in this file may or may not corelate to the order of the images in the folder.
- images/
    - folder containing the actual check images used for this competition. Image types are not guaranteed (.png/.jpg/.jpeg) nor are image sizes/resolutions.
- validation/
    - folder for images to use to validate your solution

Notes:
In our data set, the amount as text should be all lowercase
In our data set, the amount as numbers should be out to two decimal places
In our data set, the date is exactly as written
Feel free to add to the data set while building your solution

# Acknowledgements

All checks in the images have been created for the purpose of this competition and are not indicative of real checks that Citi may receive.

# Inspiration

- Can we take handwritten text and convert that into a digital form
- Can we take images and verify the amount with what is written on the check
- Can we validate the information extracted to prevent fraud


Link for the sample data set:

https://drive.google.com/file/d/1x5KuPlBIZth5FC3NgAq3_A_eA9XJUnv6/view?usp=sharing
