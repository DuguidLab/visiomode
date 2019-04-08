-- Single target, always rewarded
local composer = require( "composer" )

local scene = composer.newScene()

-- -----------------------------------------------------------------------------------
-- Code outside of the scene event functions below will only be executed ONCE unless
-- the scene is removed entirely (not recycled) via "composer.removeScene()"
-- -----------------------------------------------------------------------------------
local json = require("json")

-- initialise variables
local session

local target
local bounds
local hits
local misses
local precued
local corrections
local correction_trial -- indicateif a trial is a correction so as to not be counted

local start

local taskSettings
local sessionSettings
local sessionTimer

local iti_timer

local startTime
local hitTime
local missTime
local precueTime

local targetDistance  -- mm
local horizontalWidth

-- RPi comm buffer
local buffer

-- protocol mode
local mode


-- TODO figure out DPI at runtime!
local pixelMilliMeter = 0.2645833  -- factor for converting pixels to mm 


local function getSessionSettings()
    sessionSettings = composer.getVariable("sessionSettings")
    table.foreach(sessionSettings, print)
end

local function getTaskSettings()
    taskSettings = composer.getVariable("taskSettings")
    table.foreach(taskSettings, print)
end


local function restoreTargets()
    if taskSettings.mode == 'single_target' then
        target.alpha = 1
        return
    end

    if not correction_trial then
        -- randomly assign target/distractor positions
        local target_pos = math.random(#bounds)
        local distractor_pos = 3 - target_pos
        target.x = bounds[target_pos]
        distractor.x = bounds[distractor_pos]
    end
    
    target.alpha = 1
    distractor.alpha = 1
end


local function getITI()
    return math.random(2000, 4000)
end


local function streamEvent(event_type, touchTime, event)
    local now = os.clock()
    local event = {
            event_type = event_type,
            timestamp = touchTime,
            x_distance = event.x - event.xStart,
            y_distance = event.y - event.yStart,
            x = event.x,
            y = event.y,
            duration = now - touchTime,
            touch_force = event.pressure
        }
    composer.setVariable('buffer', {'event:' .. json.encode(event)})
end


local function onTargetHit(event)
    local target = event.target
    local phase = event.phase

    if ("began" == phase) then
        hitTime = os.clock()
    elseif ("moved" == phase) then
        return true
    elseif ("ended" == phase) then
        target.alpha = 0

        streamEvent('hit', hitTime, event)

        table.insert(hits, event)
        print("hit")

        iti_timer = timer.performWithDelay(getITI(), restoreTargets)
    end

    return true
end


local function onTargetMiss(event)
    local phase = event.phase

    if ("began" == phase) then
        missTime = os.clock()
    elseif ("moved" == phase) then

    elseif ("ended" == phase) then
        streamEvent('miss', missTime, event)

        table.insert(misses, event)
        print("miss")
        
        iti_timer = timer.performWithDelay(getITI(), restoreTargets)
    end

    return true
end


local function onPrecued(event)
    local phase = event.phase

    if ("began" == phase) then
        missTime = os.clock()
    elseif ("moved" == phase) then

    elseif ("ended" == phase) then
        streamEvent('precued', missTime, event)
        table.insert(precued, event)
        print("precued")

        -- reset ITI
        if iti_timer then
            timer.cancel(iti_timer)
        end
        iti_timer = nil
        iti_timer = timer.performWithDelay(getITI(), restoreTargets)
    end

    return true
end


local function saveSession()
    local filePath = system.pathForFile("session-" .. os.date('%Y%m%d_%H%M%S') ..  ".json", system.DocumentsDirectory)
    local file = io.open(filePath, "w")

    session = {
        timestamp = os.date('%Y-%m-%d_%H:%M:%S'),
        hits = hits,
        misses = misses,
        precued = precued
    }

    if file then
        file:write(json.encode(session))
        io.close(file)
    end
end


local function sessionEnd()
    saveSession()

    -- tell listener it's all over
    composer.setVariable(
            'buffer', {'session_end:' .. os.date('%Y%m%d_%H%M%S')}
        )

    if composer.getVariable('lastSession') then
        composer.variables['lastSession'] = nil
    end
    composer.setVariable("lastSession", session)
    composer.gotoScene("last-session-summary")
end


local function setupSingleTarget(sceneGroup)
    target = display.newImageRect(sceneGroup, "assets/stage1.jpg", 1000, 768)
    target.x = display.contentCenterX
    target.y = display.contentCenterY

    target:addEventListener("touch", onTargetHit)
end


local function setupVisualDiscrimination(sceneGroup)
    corrections = {}
    correction_trial = false

    -- offset to move everything left or right
    local offset = -25

    print(display.actualContentWidth)
    -- local dividerWidth 5 / pixelMilliMeter  -- 5 mm to pixels
    local dividerWidth = 35
    local divider = display.newRect(sceneGroup, (display.actualContentWidth * 0.5) + display.screenOriginX + offset, display.contentCenterY, dividerWidth, display.contentHeight)
    divider.fill= { 0.5, 0.5, 0.5 }


     -- set up bounds (x positions)
    bounds = {
        (display.actualContentWidth * 0.25) + display.screenOriginX  - (dividerWidth / 2) + offset,
        (display.actualContentWidth * 0.75) + display.screenOriginX + (dividerWidth / 2) + offset
    }

    local width = 665
    target = display.newImageRect(sceneGroup, 'assets/stage2_target.jpg', width, display.contentHeight)
    target.y = display.contentCenterY

    distractor = display.newImageRect(sceneGroup, 'assets/stage2_distractor.jpg', width, display.contentHeight)
    distractor.y = display.contentCenterY

    target:addEventListener("touch", onTargetHit)
    distractor:addEventListener("touch", onTargetMiss)
end

-- -----------------------------------------------------------------------------------
-- Scene event functions
-- -----------------------------------------------------------------------------------

-- create()
function scene:create( event )
    -- get settings 
    getSessionSettings()
    getTaskSettings()
    -- set msec start time
    startTime = os.clock()

    -- init tables for hits / misses
    hits = {}
    misses = {}
    precued = {}

    -- set up task scene
    local sceneGroup = self.view

    local background = display.newRect( display.contentCenterX, display.contentCenterY, display.contentWidth, display.contentHeight )
    background.fill = {0, 0, 0}
    background:toBack()


    if (taskSettings.mode == 'vdt') then
        setupVisualDiscrimination(sceneGroup)
    else
        setupSingleTarget(sceneGroup)
    end 

    print(display.contentHeight)

    background:addEventListener("touch", onPrecued)
end


-- show()
function scene:show( event )

    local sceneGroup = self.view
    local phase = event.phase

    if ( phase == "will" ) then

    elseif ( phase == "did" ) then
        if (sessionSettings.duration > 0) then
          -- gotta convert min to msec
            sessionTimer = timer.performWithDelay( sessionSettings.duration * 60000, sessionEnd, 1 )
        end
    end
end


-- hide()
function scene:hide( event )

    local sceneGroup = self.view
    local phase = event.phase

    if ( phase == "will" ) then
        timer.cancel( sessionTimer )
        saveSession()
    elseif ( phase == "did" ) then
        composer.removeScene( "task-visuomotor" )
    end
end


-- destroy()
function scene:destroy( event )

    local sceneGroup = self.view

end


-- -----------------------------------------------------------------------------------
-- Scene event function listeners
-- -----------------------------------------------------------------------------------
scene:addEventListener( "create", scene )
scene:addEventListener( "show", scene )
scene:addEventListener( "hide", scene )
scene:addEventListener( "destroy", scene )
-- -----------------------------------------------------------------------------------

return scene
