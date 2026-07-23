package com.under_pressure.mastery
{
    import flash.display.Sprite;

    /** Compatibility no-op. Marks has no mastery detail panel. */
    public class MasteryDetailPanel extends Sprite
    {
        public function MasteryDetailPanel()
        {
            super();
            visible = false;
            mouseEnabled = false;
            mouseChildren = false;
        }

        public function setLocalization(data:Object):void {}
        public function setTankInfo(tankName:String, flagText:String, stars:int, currentMark:Number):void {}
        public function setBattles(entries:Array):void {}
        public function show():void { visible = false; }
        public function hide():void { visible = false; }
        public function updateLayout():void {}
        public function dispose():void {}
    }
}
