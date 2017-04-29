function Queue(map)
{
    this.q = new Array();
    this.map = map;
}

Queue.prototype.push = function (x,y) {
    var item = new Object();
    item.x = x;
    item.y = y;
    this.q.push(item);
    this.map.blocks[y*this.map.width+x].changestate(1);
    this.map.opened++;
}

Queue.prototype.pop = function () {
    var item;
    item = this.q[0];
    this.q.splice(0,1);
    return item;
}

Queue.prototype.length = function () {
    return this.q.length;
}

function Map(parent,width,height,blocksize,nummines)
{
    this.width = width;
    this.height = height;
    this.parent = parent;
    this.blocksize = blocksize;
    this.blocks = new Array();
    
    this.marked = 0;
    this.opened = 0;
    this.totalmines = nummines;
}

Map.prototype.addblock = function (x,y) {
    var newblock = new Block(x,y,this);
    this.blocks[y*this.width+x] = newblock;
}

Map.prototype.isvalid = function (x,y) {
    if((x >= 0)&&(y >= 0)&&(x < this.width)&&(y < this.height)) {
        return true;
    }
    return false;
}

Map.prototype.checkmines = function () {
    if((this.marked == this.totalmines)&&((this.marked + this.opened) == (this.width*this.height))) {
        return true;
    } else {
        return false;
    }
}

Map.prototype.mark = function (x,y) {
    if(this.isvalid(x,y)) {
        if(this.blocks[y*this.width+x].state == 0) {
            this.blocks[y*this.width+x].changestate(2);
            this.marked++;
        } else if(this.blocks[y*this.width+x].state == 2) {
            this.blocks[y*this.width+x].changestate(0);
            this.marked--;
        }
    }
}

Map.prototype.select = function (x,y) {
    var lx,ly;
    var openerqueue = new Queue(this);
    if(this.blocks[y*this.width+x].value <= 8)
    {
        openerqueue.push(x,y);
    } else {
        this.blocks[y*this.width+x].changestate(3);
        alert("Mine Hit!");
        return;
    }
    
    while(openerqueue.length()) {
        loc = openerqueue.pop();
        lx = loc.x;
        ly = loc.y;
        if(this.isvalid(lx,ly)) {
            if((this.blocks[ly*this.width+lx].value == 0)&&(this.blocks[ly*this.width+lx].state != 2)) {
            
                if(this.isvalid(lx-1,ly-1)) {
                    if((this.blocks[(ly-1)*this.width+(lx-1)].state == 0)) openerqueue.push(lx-1,ly-1);
                }
                
                if(this.isvalid(lx-1,ly)) {
                    if((this.blocks[ly*this.width+(lx-1)].state == 0)) openerqueue.push(lx-1,ly);
                }
                
                if(this.isvalid(lx-1,ly+1)) {
                    if((this.blocks[(ly+1)*this.width+(lx-1)].state == 0)) openerqueue.push(lx-1,ly+1);
                }
                
                if(this.isvalid(lx,ly-1)) {
                    if((this.blocks[(ly-1)*this.width+lx].state == 0)) openerqueue.push(lx,ly-1);
                }
                
                if(this.isvalid(lx,ly+1)) {
                    if((this.blocks[(ly+1)*this.width+lx].state == 0)) openerqueue.push(lx,ly+1);
                }
                
                if(this.isvalid(lx+1,ly-1)) {
                    if((this.blocks[(ly-1)*this.width+(lx+1)].state == 0)) openerqueue.push(lx+1,ly-1);
                }
                
                if(this.isvalid(lx+1,ly)) {
                    if((this.blocks[ly*this.width+(lx+1)].state == 0)) openerqueue.push(lx+1,ly);
                }
                
                if(this.isvalid(lx+1,ly+1)) {
                    if((this.blocks[(ly+1)*this.width+(lx+1)].state == 0)) openerqueue.push(lx+1,ly+1);
                }
            }    
        }    
    }
}

Map.prototype.createdumbmap = function () {
    with(this) {
        for(i=0; i<width; i++) {
            for(j=0; j<height; j++) {
                addblock(i,j);
            }
        }    
    }
}

Map.prototype.randomizebombs = function () {
    for(i=0;i<this.totalmines;i++) {
        var ix = Math.floor((Math.random()*(this.width-1))+1);
        var iy = Math.floor((Math.random()*(this.height-1))+1);
        this.putbomb(ix,iy);
    }
}

Map.prototype.putbomb = function (x,y) {
    with(this) {
        if(blocks[y*width+x].value <= 8) {
            blocks[y*width+x].value = 9;
            if(isvalid(x-1,y-1)) blocks[(y-1)*width+(x-1)].value++;
            if(isvalid(x-1,y)) blocks[y*width+(x-1)].value++;
            if(isvalid(x-1,y+1)) blocks[(y+1)*width+(x-1)].value++;
            if(isvalid(x,y-1)) blocks[(y-1)*width+x].value++;
            if(isvalid(x,y+1)) blocks[(y+1)*width+x].value++;
            if(isvalid(x+1,y-1)) blocks[(y-1)*width+(x+1)].value++;
            if(isvalid(x+1,y)) blocks[y*width+(x+1)].value++;
            if(isvalid(x+1,y+1)) blocks[(y+1)*width+(x+1)].value++;
        } else {
            this.totalmines--;
        }
    }
}

function Block(x,y,map)
{
    this.x = x;
    this.y = y;
    this.id = "x"+x+"y"+y;
    this.map = map;
    this.value = 0;
    this.state = 0;
    $(map.parent).append('<div id="'+this.id+'" class="block'+this.state+'" style="left: '+x*map.blocksize+'px; top: '+y*map.blocksize+'px;"></div>');
    $("#"+this.id).bind("click", function (event) {
        var clickedid = $(this).attr("id").split("x")[1].split("y");
        var ix = parseInt(clickedid[0]);
        var iy = parseInt(clickedid[1]);
        if(event.ctrlKey) {
            newmap.mark(ix,iy);    
        } else {
            newmap.select(ix,iy);
        }
        if(newmap.checkmines()) alert("Good Work!");
    });
}

Block.prototype.changestate = function (lstate) {
    if(lstate == 1) {
        if((this.value > 0)&&(this.value < 9)) $("#"+this.id).html(this.value);
    }
    this.state = lstate;
    $("#"+this.id).attr("class","block"+lstate);
}

var newmap;

function init()
{
    newmap = new Map("#playarea",20,20,25,35);
    $(newmap.parent).width("500px");
    $(newmap.parent).height("500px");
    
    newmap.createdumbmap();
    newmap.randomizebombs();
}
