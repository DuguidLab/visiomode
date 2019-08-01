-- Single target, always rewarded
local composer = require("composer")

local scene = composer.newScene()

-- -----------------------------------------------------------------------------------
-- Code outside of the scene event functions below will only be executed ONCE unless
-- the scene is removed entirely (not recycled) via "composer.removeScene()"
-- -----------------------------------------------------------------------------------
local json = require("json")

local session

local target
local bounds
local hits
local misses
local precued
local corrections
local correctionTrial -- indicate if a trial is a correction so as to not be counted

local taskSettings
local sessionTimer

local itiTimer

local startTime
local touchTime
local presentationTime


local function getTaskSettings()
    taskSettings = composer.getVariable("taskSettings")
    table.foreach(taskSettings, print)
end

local function restoreTargets()
    presentationTime = os.clock()
    
    if taskSettings.mode == 'single_target' then
        target.alpha = 1
        return
    end

    if not correctionTrial then
        -- randomly assign target/distractor positions
        local targetPosition = math.random(#bounds)
        local distractorPosition = 3 - targetPosition
        target.x = bounds[targetPosition]
        distractor.x = bounds[distractorPosition]
    end

    target.alpha = 1
    distractor.alpha = 1
end

local function getITI()
    return math.random(taskSettings.iti_min, taskSettings.iti_max)
end

local function streamEvent(event_type, touchTime, event)
    local now = os.clock()
    local touchEvent = {
        event_type = event_type,
        timestamp = touchTime,
        x_distance = event.x - event.xStart,
        y_distance = event.y - event.yStart,
        x = event.x,
        y = event.y,
        duration = now - touchTime,
        rt = presentationTime - touchTime,
        touch_force = event.pressure
    }
    composer.setVariable('buffer', { 'event:' .. json.encode(touchEvent) })
end

local function onTargetHit(event)
    local target = event.target
    local phase = event.phase

    if ("began" == phase) then
        touchTime = os.clock()
    elseif ("moved" == phase) then
        return true
    elseif ("ended" == phase) then
        local eventType = 'hit'
        target.alpha = 0

        if taskSettings.mode == 'vdt' then
            distractor.alpha = 0
        end

        if correctionTrial then
            eventType = 'correction_hit'
            table.insert(corrections, hit)
            correctionTrial = false
        else
            table.insert(hits, event)
            print("hit")
        end

        streamEvent(eventType, touchTime, event)
        itiTimer = timer.performWithDelay(getITI(), restoreTargets)
    end

    return true
end

local function onTargetMiss(event)
    local phase = event.phase

    if ("began" == phase) then
        touchTime = os.clock()
    elseif ("moved" == phase) then

    elseif ("ended" == phase) then
        local event_type = 'miss'
        target.alpha = 0

        if taskSettings.mode == 'vdt' then
            distractor.alpha = 0

            -- correction trials
            if correctionTrial then
                event_type = 'correction'
                table.insert(corrections, event)
                print("still correcting")
            else
                event_type = 'miss'
                table.insert(misses, event)
                print("miss")
                correctionTrial = true -- next trial should be a correction trial
            end
        end

        streamEvent(event_type, touchTime, event)
        itiTimer = timer.performWithDelay(getITI(), restoreTargets)
    end

    return true
end

local function onPrecued(event)
    local phase = event.phase

    if ("began" == phase) then
        touchTime = os.clock()
    elseif ("moved" == phase) then

    elseif ("ended" == phase) then
        streamEvent('precued', touchTime, event)
        table.insert(precued, event)
        print("precued")

        -- reset ITI
        if itiTimer then
            timer.cancel(itiTimer)
        end
        itiTimer = nil
        itiTimer = timer.performWithDelay(getITI(), restoreTargets)
    end

    return true
end

local function saveSession()
    local filePath = system.pathForFile("session-" .. os.date('%Y%m%d_%H%M%S') .. ".json", system.DocumentsDirectory)
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
            'buffer', { 'session_end:' .. os.date('%Y%m%d_%H%M%S') }
    )

    if composer.getVariable('lastSession') then
        composer.variables['lastSession'] = nil
    end
    composer.setVariable("lastSession", session)
    composer.gotoScene("last-session-summary")
end

local function setupSingleTarget(sceneGroup)
    target = display.newGroup()
    local frame1 = display.newImageRect(sceneGroup, "assets/stage1.jpg", 1000, 768)
    local frame2 = display.newImageRect(sceneGroup, "assets/stage1.jpg", 1000, 768)

    frame1.y = display.contentCenterY + 384
    frame2.y = display.contentCenterY - 384

    transition.to( frame1, { time=1000, y=384, iterations=0 } )
    transition.to( frame2, { time=1000, y=-384, iterations=0 } )

    target:insert(frame1)
    target:insert(frame2)
    --target = display.newImageRect(sceneGroup, "assets/stage1.jpg", 1000, 768)
    target.x = display.contentCenterX

    target:addEventListener("touch", onTargetHit)
end

local function setupVisualDiscrimination(sceneGroup)
    corrections = {}
    correctionTrial = false

    -- offset to move everything left or right
    local offset = taskSettings.offset

    print(display.actualContentWidth)
    -- local dividerWidth 5 / pixelMilliMeter  -- 5 mm to pixels
    local dividerWidth = 200
    local divider = display.newRect(sceneGroup, (display.actualContentWidth * 0.5) + display.screenOriginX + offset,
            display.contentCenterY, dividerWidth, display.contentHeight)
    divider.fill = { 0, 0, 0 }
    divider:addEventListener("touch", function () return true end)


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
    --target = display.newImageRect(sceneGroup, 'assets/stage2_target.jpg', width, display.contentHeight)
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
function scene:create(event)
    -- get settings 
    getTaskSettings()
    -- set msec start time
    startTime = os.clock()

    -- init tables for hits / misses
    hits = {}
    misses = {}
    precued = {}

    -- set up task scene
    local sceneGroup = self.view

    local background = display.newRect(sceneGroup, display.contentCenterX, display.contentCenterY, display.contentWidth, display.contentHeight)
    background.fill = { 0, 0, 0 }
    background:toBack()

    if (taskSettings.mode == 'vdt') then
        setupVisualDiscrimination(sceneGroup)
    else
        setupSingleTarget(sceneGroup)
    end

    print(display.contentHeight)

    background:addEventListener("touch", onPrecued)

    restoreTargets()
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
        saveSession()
    elseif (phase == "did") then
        transition.cancel()
        target:removeSelf()
        timer.cancel(sessionTimer)
        timer.cancel(itiTimer)
        composer.removeScene("task-visuomotor")
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
