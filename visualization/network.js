var width = window.innerWidth, 
    height = window.innerHeight;

var dist = (width + height) / 20;

var force = d3.layout.force()
    .size([width, height])
    .linkDistance(dist)
    .on("tick", stepForce)
    .alpha(.05);

var drag = force.drag()
    .on("dragstart", dragstart);

var svg = d3.select("div").append("svg")
    .attr("width", width)
    .attr("height", height);

var link = svg.selectAll(".link"),
    node = svg.selectAll(".node");
    

function getedgecolor(val){
    if (val==1){return "blue";}
    else{ return "#F0F0F0";}
    }
    
function getedgeweight(val){
    return (Math.sqrt((val*20)+1));
    }

function stepForce() {

      link.attr("x1", function(d) { return d.source.x; })
        .attr("y1", function(d) { return d.source.y; })
        .attr("x2", function(d) { return d.target.x; })
        .attr("y2", function(d) { return d.target.y; });

      node.attr("cx", function(d) { return d.x; })
        .attr("cy", function(d) { return d.y; });
}

function dragstart(d) {
  d.fixed = true;
  d3.select(this).classed("fixed", true);
}


d3.json("fbgraph.json", function(error, graph) {
  
  var k = Math.sqrt(graph.nodes.length / (width * height))
  
  force
      .nodes(graph.nodes)
      .links(graph.links)
      .gravity(65*k)
      .charge(-18/k)
      .start();

  link = link.data(graph.links)
    .enter().append("line")
      .attr("class", "link")
      .style("stroke", function(d) { return getedgecolor(d.strong);} )
      .style("stroke-width", function(d) { return getedgeweight(d.weight);})
      .on("click", function(d) { return d.n1 });
    
  link.append("title")
      .text(function(d) { return "Tie: "+d.n1+ " & "+d.n2+":Str="+d.strong+" & Wght="+d.weight; })

  node = node.data(graph.nodes)
    .enter().append("circle")
      .attr("class", "node")
      .attr("r", 7)
      .style("fill", function(d) { return d.color })
      .style("stroke", "black")
      .style("opacity", 0.8)
      .text(function(d) { return d.name })
      .on("dblclick",function(d) {
            if ( confirm('This is '+d.name+". Do you want to unstick them?" ) ) 
               d.fixed = false;})
      .call(drag);
      
  node.append("title")
      .text(function(d) { return d.name+" : "+d.value+" mutuals" ; })
});


d3.select('#stop').on('click', function() {

    //If we've already started the layout, stop it.
    if (force) {
        force.stop();
    }
  });

d3.select('#play').on('click', function() {
    // Get the animation rolling

    force.start();

});