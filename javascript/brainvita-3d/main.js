function Map(viewmap)
{
    this.viewmap = viewmap;
    this.selected = undefined;
    this.blocks = new Array();
}

Map.prototype.addblock = function (x,y,state) {
    var newblock = new Block(x,y,state,this,this.viewmap);
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
            clearquad();
            selected = undefined;
        }
        checkima();
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

Map.prototype.checkima = function () {
    var x, y, state;
    var count = 0;
    for (key in this.blocks) {
        x = this.blocks[key].x;
        y = this.blocks[key].y;
        state = this.blocks[key].state;
        if((state == 1)&&(this.getstate(x-2,y) == 0)&&(this.getstate(x-1,y) == 1)) break;
        if((state == 1)&&(this.getstate(x+2,y) == 0)&&(this.getstate(x+1,y) == 1)) break;
        if((state == 1)&&(this.getstate(x,y-2) == 0)&&(this.getstate(x,y-1) == 1)) break;
        if((state == 1)&&(this.getstate(x,y+2) == 0)&&(this.getstate(x,y+1) == 1)) break;
        count++;
    }
    if(count == this.blocks.length) alert("No moves available...");
}

function Block(x,y,state,map,viewmap)
{
    this.x = x;
    this.y = y;
    this.id = "x"+x+"y"+y;
    this.state = state;
    
    this.map = map;
    viewmap.place(this.id, "block"+this.state, this.x, this.y);
    //$(map.parent).append('<div id="'+this.id+'" class="block'+state+'" style="position: absolute; left: '+x*map.blocksize+'px; top: '+y*map.blocksize+'px; width: '+map.blocksize+'px; height: '+map.blocksize+'px;"></div>');
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

function BaseMap(gleft, gtop, gwidth, gheight, grows, gcols, gzmax, gyscale)
{
    this.left = gleft;
    this.top = gtop;
    this.width = gwidth;
    this.height = gheight;
    
    this.rows = grows;
    this.cols = gcols;
    
    this.zmax = gzmax;
    this.yscale = gyscale;
    
    this.frames = new Array();
}

BaseMap.prototype.generatemap = function () {
    with(this) {
        for(i=0;i<rows;i++) {
            var newframe = new Frame(i,this);
            newframe.movetoz(-i);
            frames.push(newframe);
            //newframe.draw();
        }
    }
}

BaseMap.prototype.place = function (divid, dclass, x, y) {
    with(this) {
        var elementsize = frames[rows-y-1].width / (1.7 * cols);
        var elementleft = frames[rows-y-1].left + x * 1.7 * elementsize;
        var elementtop = frames[rows-y-1].top + frames[rows-y-1].height - elementsize;
        $("body").append('<div id="'+divid+'" class="'+dclass+'" style="position: absolute; width: '+elementsize+'px; height: '+elementsize+'px; left: '+elementleft+'px; top: '+elementtop+'px;"></div>')
    }
}

function Frame(id,basemap)
{
    this.id = id;
    this.z = 0;
    this.basemap = basemap;
    this.left = basemap.left;
    this.top = basemap.top;
    this.width = basemap.width;
    this.height = basemap.height;
}

Frame.prototype.movetoz = function (Znew) {
    with(this) {
        var lold = basemap.zmax + z;
        var lnew = basemap.zmax + Znew;
        var Wnew = width * (lnew/lold);
        var Hnew = height * (lnew/lold);
        
        z = Znew;
        left = left + (width - Wnew)/2;
        top = top - basemap.yscale*(width - Wnew)*lnew/Wnew;
        width = Wnew;
        height = Hnew;
    }
}

Frame.prototype.draw = function () {
    with(this) {
        $("body").append('<div id="'+id+'" style="position: absolute; border: 1px solid black; width: '+width+'px; height: '+height+'px; left: '+left+'px; top: '+top+'px;"></div>')
    }
}

var newbasemap = new BaseMap(100, 350, 800, 200, 7, 7, 14, 45);
var newmap = new Map(newbasemap);

function init(frames)
{
    newbasemap.generatemap();
    //var stringmap = "9,9,2,2,2,1,1,1,2,2,2,2,2,2,1,1,1,2,2,2,2,2,2,1,1,1,2,2,2,1,1,1,1,1,1,1,1,1,1,1,1,1,0,1,1,1,1,1,1,1,1,1,1,1,1,1,2,2,2,1,1,1,2,2,2,2,2,2,1,1,1,2,2,2,2,2,2,1,1,1,2,2,2";
    var stringmap = "7,7,2,2,1,1,1,2,2,2,2,1,1,1,2,2,1,1,1,1,1,1,1,1,1,1,0,1,1,1,1,1,1,1,1,1,1,2,2,1,1,1,2,2,2,2,1,1,1,2,2";
    newmap.createmap(stringmap);
    //newbasemap.drawmap(stringmap);
}
