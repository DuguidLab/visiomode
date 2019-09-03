-- Single target, always rewarded
local composer = require("composer")

local scene = composer.newScene()

-- -----------------------------------------------------------------------------------
-- Code outside of the scene event functions below will only be executed ONCE unless
-- the scene is removed entirely (not recycled) via "composer.removeScene()"
-- -----------------------------------------------------------------------------------
local target

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
    target.x = display.contentCenterX
end

-- -----------------------------------------------------------------------------------
-- Scene event functions
-- -----------------------------------------------------------------------------------

-- create()
function scene:create(event)
    -- set up task scene
    local sceneGroup = self.view

    local background = display.newRect(sceneGroup, display.contentCenterX, display.contentCenterY, display.contentWidth, display.contentHeight)
    background.fill = { 0, 0, 0 }
    background:toBack()

    setupSingleTarget(sceneGroup)
end


-- show()
function scene:show(event)

    local sceneGroup = self.view
    local phase = event.phase

    if (phase == "will") then

    elseif (phase == "did") then

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
