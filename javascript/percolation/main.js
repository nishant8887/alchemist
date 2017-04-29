function Map(parent,width,height,blocksize)
{
    this.width = width;
    this.height = height;
    this.parent = parent;
    this.blocksize = blocksize;
    this.blocks = new Array();
    this.boxes = new Array(width*height+2);
    this.totalopened = 0;
}

Map.prototype.root = function (e) {
    while (this.boxes[e] != e) {
        e = this.boxes[e];
    }
    return e;
}

Map.prototype.union = function (e1, e2) {
    this.boxes[this.root(e1)] = this.root(e2);
}

Map.prototype.find = function (e1, e2) {
    if(this.root(e1) == this.root(e2)) {
        return true;
    }
    else {
        return false;
    }
}

Map.prototype.generatestream = function () {
    var maxpercolation = 0;
    var curry;
    for(k = 0; k < this.width * this.height; k++) {
        if(this.root(this.width*this.height) == this.root(k)) {
            if(this.blocks[k].state == 0) {
                this.blocks[k].changestate(2);
            }
            curry = Math.floor(k/this.width);
            if(maxpercolation < curry) maxpercolation = curry;
        }
    }
    drawpoint(this.totalopened,maxpercolation);
}

Map.prototype.isvalidandempty = function (x,y) {
    if((x >= 0)&&(y >= 0)&&(x < this.width)&&(y < this.height)) {
        if(this.blocks[y*this.width+x].state != 1) {
            return true;    
        }
    }
    return false;
}

Map.prototype.addblock = function (x,y) {
    var newblock = new Block(x,y,this);
    this.blocks[y*this.width+x] = newblock;
    this.boxes[y*this.width+x] = y*this.width+x;
}

Map.prototype.createmap = function () {
    with(this) {
        this.boxes[this.height*this.width] = this.height*this.width;
        this.boxes[this.height*this.width+1] = this.height*this.width+1;
        for(i=0; i<width; i++) {
            for(j=0; j<height; j++) {
                addblock(i,j);
            }
        }
        for(i=0; i<width; i++) {
            this.union(i, this.width*this.height);
            this.union((height - 1)*this.width+i, this.width*this.height+1);
        }
    }
}

Map.prototype.randomlyopensite = function () {
    var ix = Math.floor((Math.random()*this.width));
    var iy = Math.floor((Math.random()*this.height));
    if(this.blocks[iy*this.width+ix].state == 1) {
        this.blocks[iy*this.width+ix].changestate(0);
        if(this.isvalidandempty(ix-1,iy)) this.union(iy*this.width+ix, iy*this.width+(ix-1));
        if(this.isvalidandempty(ix+1,iy)) this.union(iy*this.width+ix, iy*this.width+(ix+1));
        if(this.isvalidandempty(ix,iy-1)) this.union(iy*this.width+ix, (iy-1)*this.width+ix);
        if(this.isvalidandempty(ix,iy+1)) this.union(iy*this.width+ix, (iy+1)*this.width+ix);
        this.totalopened++;
        this.generatestream();
    }

    if(this.find(this.width*this.height,this.width*this.height+1)) {
        console.log(this.totalopened/(this.width*this.height));
        console.log("Path generated");
        window.clearInterval(timer);
    }
}

function Block(x,y,map)
{
    this.x = x;
    this.y = y;
    this.id = "x"+x+"y"+y;
    this.map = map;
    this.state = 1;
    $(map.parent).append('<div id="'+this.id+'" class="block'+this.state+'" style="position: absolute; left: '+x*map.blocksize+'px; top: '+y*map.blocksize+'px; width: '+map.blocksize+'px; height: '+map.blocksize+'px;"></div>');
}

Block.prototype.changestate = function (lstate) {
    this.state = lstate;
    $("#"+this.id).attr("class","block"+lstate);
}

function drawpoint(x,y)
{
    var ctx = document.getElementById("graph").getContext("2d");
    ctx.lineTo(x,100-10*y);
    ctx.stroke();
}

var newmap;
var timer;

function init()
{
    newmap = new Map("#box",10,10,10);
    $(newmap.parent).width("100px");
    $(newmap.parent).height("100px");
    
    newmap.createmap();
    timer = window.setInterval(function () { newmap.randomlyopensite(); },10);
}
