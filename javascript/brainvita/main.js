function Map(parent,blocksize)
{
    this.parent = parent;
    this.blocksize = blocksize;
    this.selected = undefined;
    this.blocks = new Array();
}

Map.prototype.addblock = function (x,y,state) {
    var newblock = new Block(x,y,state,this);
    this.blocks.push(newblock);
}

Map.prototype.findblock = function (x,y) {
    with(this){
        for(key in blocks) {
            if((blocks[key].x == x)&&(blocks[key].y == y)) return key;
        }
        return undefined;
    }
}

Map.prototype.getstate = function (x,y) {
    var wblock = this.findblock(x,y);
    if(wblock) {
        return this.blocks[wblock].state;
    } else {
        return undefined;
    }
}

Map.prototype.setstate = function (x,y,state) {
    var wblock = this.findblock(x,y);
    if(wblock) this.blocks[wblock].changestate(state);
}

Map.prototype.clearquad = function () {
    with(this)
    {
        var ix, iy;
        if(selected) {
            ix = blocks[selected].x;
            iy = blocks[selected].y;
            setstate(ix,iy,5);
            setstate(ix-2,iy,5);
            setstate(ix+2,iy,5);
            setstate(ix,iy-2,5);
            setstate(ix,iy+2,5);    
        }
    }
}

Map.prototype.setquad = function (x,y) {
    with(this)
    {
        setstate(x,y,7);
        if(getstate(x-1,y) == 1) setstate(x-2,y,6);
        if(getstate(x+1,y) == 1) setstate(x+2,y,6);
        if(getstate(x,y-1) == 1) setstate(x,y-2,6);
        if(getstate(x,y+1) == 1) setstate(x,y+2,6);
    }
}

Map.prototype.select = function (x,y) {
    with(this) {
        var ix, iy;
        var state = getstate(x,y);
        if(state == 1) {
            var wblock = findblock(x,y);
            clearquad();
            setquad(x,y);
            selected = wblock;
        } else if(state == 0) {
            if(selected) {
                clearquad();
                ix = blocks[selected].x;
                iy = blocks[selected].y;
                if((ix + 2 == x)&&(iy == y)) blocks[selected].moveright();
                if((ix - 2 == x)&&(iy == y)) blocks[selected].moveleft();
                if((ix == x)&&(iy + 2 == y)) blocks[selected].movedown();
                if((ix == x)&&(iy - 2 == y)) blocks[selected].moveup();
                selected = undefined;
            }
        } else {
            selected = undefined;
        }
    }
}

Map.prototype.createmap = function (stringmap) {
    var localmap = stringmap.split(",");
    var lwidth = localmap[0];
    var lheight = localmap[1];
    var lstate;
    
    for(i=0; i<lwidth; i++) {
        for(j=0; j<lheight; j++) {
            lstate = parseInt(localmap[lwidth*j+i+2]);
            this.addblock(i,j,lstate);
        }
    }
}

function Block(x,y,state,map)
{
    this.x = x;
    this.y = y;
    this.id = "x"+x+"y"+y;
    this.state = state;
    
    this.map = map;
    $(map.parent).append('<div id="'+this.id+'" class="block'+state+'" style="position: absolute; left: '+x*map.blocksize+'px; top: '+y*map.blocksize+'px; width: '+map.blocksize+'px; height: '+map.blocksize+'px;"></div>');
    $("#"+this.id).on("click", function () {
        var clickedid = $(this).attr("id").split("x")[1].split("y");
        var ix = parseInt(clickedid[0]);
        var iy = parseInt(clickedid[1]);
        newmap.select(ix,iy);
    });
}

Block.prototype.changestate = function (istate) {
    var statevar = "block"+this.state;
    switch(istate)
    {
        case 5:
            break;
        case 6:
            if(!this.state) statevar = "block6";
            break;
        case 7:
            if(this.state) statevar = "block7"
            break;
        default:
            this.state = istate;
            statevar = "block"+this.state;
    }
    $("#"+this.id).attr("class",statevar);
}

Block.prototype.moveleft = function () {
    with(this) {
        if((state == 1)&&(map.getstate(x-2,y) == 0)&&(map.getstate(x-1,y) == 1)) {
            map.setstate(x,y,0);
            map.setstate(x-2,y,1);
            map.setstate(x-1,y,0);
        }
    }
}

Block.prototype.moveright = function () {
    with(this) {
        if((state == 1)&&(map.getstate(x+2,y) == 0)&&(map.getstate(x+1,y) == 1)) {
            map.setstate(x,y,0);
            map.setstate(x+2,y,1);
            map.setstate(x+1,y,0);
        }
    }
}

Block.prototype.moveup = function () {
    with(this) {
        if((state == 1)&&(map.getstate(x,y-2) == 0)&&(map.getstate(x,y-1) == 1)) {
            map.setstate(x,y,0);
            map.setstate(x,y-2,1);
            map.setstate(x,y-1,0);
        }
    }
}

Block.prototype.movedown = function () {
    with(this) {
        if((state == 1)&&(map.getstate(x,y+2) == 0)&&(map.getstate(x,y+1) == 1)) {
            map.setstate(x,y,0);
            map.setstate(x,y+2,1);
            map.setstate(x,y+1,0);
        }
    }
}

var newmap;

function init()
{
    newmap = new Map("#playarea",50);
    $(newmap.parent).width("620px");
    $(newmap.parent).height("620px");
    
    var stringmap = "9,9,2,2,2,1,1,1,2,2,2,2,2,2,1,1,1,2,2,2,2,2,2,1,1,1,2,2,2,1,1,1,1,1,1,1,1,1,1,1,1,1,0,1,1,1,1,1,1,1,1,1,1,1,1,1,2,2,2,1,1,1,2,2,2,2,2,2,1,1,1,2,2,2,2,2,2,1,1,1,2,2,2";
    newmap.createmap(stringmap);
}