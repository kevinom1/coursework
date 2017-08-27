#
# Description: Read csv file with two columns of data and plot histograms for the data 
# in each column plus a scatterplot of the two columns
# Also available at https://komahony.shinyapps.io/datavizassign1
#
# Required packages:
#   shiny
#   shinydashboard
#
# Author: Kevin O'Mahony
#
# History: 
#   13/10/2016    Original V1.0

library(shiny)
library(shinydashboard)

sideBar = dashboardSidebar(
  
  fileInput('file1', 'Choose file to upload',
            accept = c(
              'text/csv',
              'text/comma-separated-values',
              'text/tab-separated-values',
              'text/plain',
              '.csv',
              '.tsv')),
  
  # postpone rendering other controls in sidebar until data file loaded
  uiOutput("my_sidebar_controls")
)

body = dashboardBody(
  
  # experiment with navy rather than default black
  tags$head(tags$style(HTML('
      .skin-red .main-sidebar {
        background-color: #000033;
        }
    '))),
  
  # postpone rendering plot box containers until data file loaded
  uiOutput("my_plots")
)

# Put all components together to make the dashboard page
ui = dashboardPage(
  skin = 'red',
  dashboardHeader(title = ("Two Variable Exploration"), titleWidth = 450),
  sideBar, 
  body
)

server = function(input, output) {

  filedata = reactive({
    # check if a file is selected, if it isn't then do nothing
    inFile = input$file1
    if (is.null(inFile))   
      return(NULL)
    
    # otherwise load specified file as dataframe into filedata
    read.csv(inFile$datapath, header = TRUE, sep = ",")
  })
  
  output$my_sidebar_controls = renderUI({
    # check if a file is selected, if it isn't then do nothing
    inFile = input$file1
    if (is.null(inFile))   
      return(NULL)    

    # else get column names 
    x = filedata()[,1]
    y = filedata()[,2]
    xlabel = names(filedata())[1]
    ylabel = names(filedata())[2]
    s1 = paste("Set number of",xlabel,"bins")
    s2 = paste("Set number of",ylabel,"bins")
    s3 = c(paste(xlabel,"versus",ylabel),paste(ylabel,"versus",xlabel))  
    
    # create sidebar controls
    tagList(
      br(),
      sliderInput("binsX", s1, min = 1, max = 100, value = 30),
      sliderInput("binsY", s2, min = 1, max = 100, value = 30),
      br(),
      br(),
      selectInput("axesSeln", label = "Select ScatterPlot Axes",selected=1,
                                       choices=as.list(s3))
    )
  })
  
  output$my_plots = renderUI({
    # check if a file is selected, if it isn't then do nothing
    inFile = input$file1
    if (is.null(inFile))   
      return(NULL)    
    
    # else render create box components to contain plots
    tagList(
      box(status = "primary", plotOutput("plotX", height = 350)),
      box(status = "primary", plotOutput("plotY", height = 350)),
      box(status = "primary", plotOutput("plotXY", height = 350), width = 12)
    )      
  })
  
  output$plotX = renderPlot({
    # check if a file is selected, if it isn't then do nothing
    inFile = input$file1
    if (is.null(inFile))
      return(NULL)
    
    # else create histogram for data in first column in data frame
    x = filedata()[,1]
    xlabel = names(filedata())[1]
    binsForx = seq(min(x), max(x), length.out = input$binsX + 1)
    hist(x, breaks = binsForx, col = 'blue', border = 'white', xlab = xlabel, main=paste("Histogram of",xlabel))
  }) 
   
  output$plotY = renderPlot({
    # check if a file is selected, if it isn't then do nothing
    inFile = input$file1
    if (is.null(inFile))
      return(NULL)
  
    # else create histogram for data in second column in data frame
    y = filedata()[,2]
    ylabel = names(filedata())[2]
    binsForY = seq(min(y), max(y), length.out = input$binsY + 1)
    hist(y, breaks = binsForY, col = 'red', border = 'white', xlab = ylabel, main=paste("Histogram of",ylabel))
  })
  
  output$plotXY = renderPlot({
    # check if a file is selected, if it isn't then do nothing
    inFile = input$file1
    if (is.null(inFile))
      return(NULL)
    
    # else create scatter plot for data in column one and two in data frame
    x = filedata()[,1]
    y = filedata()[,2]
    xlabel = names(filedata())[1]
    ylabel = names(filedata())[2]
    
    # switch axis based on control setting
    if (input$axesSeln == paste(ylabel,"versus",xlabel))
    {
      t1 = paste("ScatterPlot of ", ylabel, "vs.", xlabel)
      plot(y, x, xlab = ylabel, ylab = xlabel, type = 'p', main = t1, col = 'blue')
      abline(lm(x ~ y), col='red')
    }
    else
    {
      t2 = paste("ScatterPlot of ", xlabel, "vs.", ylabel)
      plot(x, y, xlab = xlabel, ylab = ylabel, type = 'p', main = t2, col = 'blue')
      abline(lm(y ~ x), col='red')
    }
  })
}

shinyApp(ui, server)