-- Grating and gray stimulus presentation
local composer = require("composer")
local json = require("json")

local scene = composer.newScene()


-- -----------------------------------------------------------------------------------
-- Code outside of the scene event functions below will only be executed ONCE unless
-- the scene is removed entirely (not recycled) via "composer.removeScene()"
-- -----------------------------------------------------------------------------------
local target
local distractor
local session
local startTime
local presentationTime
local cycleTimer

local taskSettings
local sessionTimer

local ipiTimer  -- inter-presentation timer


local function getTaskSettings()
    taskSettings = composer.getVariable("taskSettings")
    table.foreach(taskSettings, print)
end

local function getIPI()
    return math.random(taskSettings.iti_min, taskSettings.iti_max)
end

local function streamCycle(timestamp, ipi, duration)
    local touchEvent = {
        event_type = 'stim2',
        timestamp = timestamp,
        duration = duration,
        ipi = ipi,
    }
    composer.setVariable('buffer', { 'event:' .. json.encode(touchEvent) })
end

local function setupStimuli(sceneGroup)
    -- offset to move everything left or right
    local offset = taskSettings.offset

    print(display.actualContentWidth)
    -- local dividerWidth 5 / pixelMilliMeter  -- 5 mm to pixels
    local dividerWidth = 100
    local divider = display.newRect(sceneGroup, (display.actualContentWidth * 0.5) + display.screenOriginX + offset,
            display.contentCenterY, dividerWidth, display.contentHeight)
    divider.fill = { 0, 0, 0 }

    -- set up bounds (x positions)
    bounds = {
        (display.actualContentWidth * 0.25) + display.screenOriginX - (dividerWidth / 3) + offset,
        (display.actualContentWidth * 0.75) + display.screenOriginX + (dividerWidth / 3) + offset
    }

    local width = 665
    target = display.newGroup(sceneGroup)
    local frame1 = display.newImageRect(sceneGroup, "assets/stage2_target.jpg", width, display.contentHeight)
    local frame2 = display.newImageRect(sceneGroup, "assets/stage2_target.jpg", width, display.contentHeight)

    frame1.y = display.contentCenterY + 384
    frame2.y = display.contentCenterY - 384

    transition.to( frame1, { time=1000, y=384, iterations=0 } )
    transition.to( frame2, { time=1000, y=-384, iterations=0 } )

    target:insert(frame1)
    target:insert(frame2)
    target.y = display.contentCenterY

    distractor = display.newImageRect(sceneGroup, 'assets/stage2_distractor.jpg', width, display.contentHeight)
    distractor.y = display.contentCenterY

    target.x = bounds[1]
    distractor.x = bounds[2]
end

local function showStimuli()
    target.alpha = 1
    distractor.alpha = 1
end

local function hideStimuli()
    target.alpha = 0
    distractor.alpha = 0
end

local function cycleTarget()
    local ipi = getIPI()
    local stimDuration = 2000
    local cycleDuration = stimDuration + ipi
    local now = system.getTimer()
    local ts = now - startTime
    print("thing")
    streamCycle(ts, ipi, stimDuration)
    showStimuli()
    ipiTimer = timer.performWithDelay(stimDuration, hideStimuli)
    cycleTimer = timer.performWithDelay(cycleDuration, cycleTarget)
end

local function saveSession()
    local filePath = system.pathForFile(
            "session-" .. os.date('%Y%m%d_%H%M%S') .. ".json", system.DocumentsDirectory)
    local file = io.open(filePath, "w")

    session = {
        timestamp = os.date('%Y-%m-%d_%H:%M:%S'),
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
            'buffer', { 'session_end:' .. os.date('%Y%m%d_%H%M%S') }
    )
    composer.gotoScene("menu")
end

-- -----------------------------------------------------------------------------------
-- Scene event functions
-- -----------------------------------------------------------------------------------

-- create()
function scene:create(event)
    -- set up task scene
    local sceneGroup = self.view
    startTime = system.getTimer()
    getTaskSettings()

    local background = display.newRect(sceneGroup, display.contentCenterX, display.contentCenterY, display.contentWidth, display.contentHeight)
    background.fill = { 0, 0, 0 }
    background:toBack()

    setupStimuli(sceneGroup)
    cycleTarget()
end


-- show()
function scene:show(event)

    local sceneGroup = self.view
    local phase = event.phase

    if (phase == "will") then

    elseif (phase == "did") then
         if (taskSettings.duration > 0) then
            -- gotta convert min to msec
            sessionTimer = timer.performWithDelay(taskSettings.duration * 60000, sessionEnd, 1)
        end
    end
end


-- hide()
function scene:hide(event)

    local sceneGroup = self.view
    local phase = event.phase

    if (phase == "will") then

    elseif (phase == "did") then
        transition.cancel()
        target:removeSelf()
        timer.cancel(sessionTimer)
        timer.cancel(cycleTimer)
        timer.cancel(ipiTimer)
        composer.removeScene("stim-presentation")
    end
end


-- destroy()
function scene:destroy(event)

    local sceneGroup = self.view

end


-- -----------------------------------------------------------------------------------
-- Scene event function listeners
-- -----------------------------------------------------------------------------------
scene:addEventListener("create", scene)
scene:addEventListener("show", scene)
scene:addEventListener("hide", scene)
scene:addEventListener("destroy", scene)
-- -----------------------------------------------------------------------------------

return scene
