    var frozenNode = null;
    function init() {
       BrowserDetect.init();
       var edgesArray = getEdges();
       for (i in edgesArray) {
         processEdge(edgesArray[i]);
       }
       var nodesArray = getNodes();
       for (i in nodesArray) {
         processNode(nodesArray[i]);
       }
    }
    function get_path(edge_group) {
       var anchor = edge_group.getElementsByTagName('a')[0];
       if (anchor != undefined) {
         return anchor.getElementsByTagName('path')[0];
       } else {
         return edge_group.getElementsByTagName('path')[0];
       }
    }
    function processEdge(edge_group) {   
       var path = get_path(edge_group);
       var title = edge_group.getElementsByTagName('title').item(0).childNodes.item(0).data;
       var nodes = title.split('->');
	   edge_group.setAttribute("fromnode", nodes[0]);
	   edge_group.setAttribute("tonode", nodes[1]);
       for (i in nodes) {
          nodes[i] = "'" + nodes[i] +"'";
       }
       edge_group.setAttribute("onmouseover", "line_over(evt, [" +nodes.join(', ')+"])");
       edge_group.setAttribute("onmouseout", "line_out(evt, [" +nodes.join(', ')+"])");
    }
    function processNode(node_group) {
       var title = node_group.getElementsByTagName('title').item(0).childNodes.item(0).data;
	   var targetEdges = getEdgesWithTargetNode(title);
	   var targetEdgeNames = new Array;
       for (i in targetEdges) {
          targetEdgeNames.push("'" + targetEdges[i].getAttribute("id") +"'");
       }
	   var sourceEdges = getEdgesWithSourceNode(title);
	   var sourceEdgeNames = new Array;
       for (i in sourceEdges) {
          sourceEdgeNames.push("'" + sourceEdges[i].getAttribute("id") +"'");
       }
       node_group.setAttribute("onmouseover", "node_line_over(evt, [" +targetEdgeNames.join(', ')+"], [" +sourceEdgeNames.join(', ')+"])");
       node_group.setAttribute("onmouseout", "node_line_out(evt, [" +targetEdgeNames.join(', ')+"], [" +sourceEdgeNames.join(', ')+"])");
       if ((BrowserDetect.browser == 'Firefox') || (BrowserDetect.browser == 'Mozilla')) {
	       node_group.setAttribute("onclick", "freeze_node(evt)");
       } else {
	       node_group.setAttribute("onactivate", "freeze_node(evt)");
	   }
	}
	
	  
	function freeze_node(evt) {
	  var node_group = get_group(evt.target);
	  if (node_group == frozenNode) {
	    frozenNode = null;
	    eval(node_group.getAttribute("onmouseout"));
	  } else {
	    if (frozenNode != null) {
	      var tempFrozenNode = frozenNode;
  	      frozenNode = null; 
  	      var evt = {target: tempFrozenNode};
	      eval(tempFrozenNode.getAttribute("onmouseout"));
	      evt = {target: node_group};
	      eval(node_group.getAttribute("onmouseover"));
	    }
	    frozenNode = node_group;
	  }
	}
	function getEdgesWithTargetNode(title) {
	  var iterator = document.evaluate("//svg:g[@class='edge' and @tonode='" +title+"']", document, nslookup,
			XPathResult.ORDERED_NODE_ITERATOR, null);
	  return iteratorToArray(iterator);
	}
	function getEdgesWithSourceNode(title) {
	  var iterator = document.evaluate("//svg:g[@class='edge' and @fromnode='" +title+"']", document, nslookup,
			XPathResult.ORDERED_NODE_ITERATOR, null);
	  return iteratorToArray(iterator);
	}
    function store_attributes(element, attributes) {
       for (i in attributes) {
       	  if (!element.hasAttribute("old-" + attributes[i])) {
            element.setAttribute("old-" + attributes[i], element.getAttribute(attributes[i]));
          }
       }
    }
    function restore_attributes(element, attributes) {
       for (i in attributes) {
         element.setAttribute(attributes[i], element.getAttribute("old-" + attributes[i]));
       }
    }
	function nslookup(prefix) {
        var svgPrefix = svgPrefix || 'svg';
          var namespaceResolver = document.createNSResolver(document.documentElement);
          switch (prefix) {
            case svgPrefix:
              return 'http://www.w3.org/2000/svg';
            default:
              return namespaceResolver.lookupNamespaceURI(prefix);
          }
        }
    function getNodeByTitle(title) {
        return document.evaluate("//svg:g[@class='node' and svg:title='" + title + "']", document, nslookup,      
			XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
    }
    function getEdgeById(id) {
        return document.evaluate("//svg:g[@class='edge' and @id='" + id + "']", document, nslookup,      
			XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
    }
	function getGroups(class_name) {
        return document.evaluate("//svg:g[@class='" + class_name + "']", document, nslookup,
			XPathResult.ORDERED_NODE_ITERATOR, null);
	}
	function iteratorToArray(iterator) {
        var group;
        var groupsArray = new Array();
        while ((group = iterator.iterateNext()) != null) {
          groupsArray.push(group);
        }
		return groupsArray;
	}
	function getGroupsAsArray(class_name) {
	    var iterator = getGroups(class_name);
		return iteratorToArray(iterator);
	}
    function getEdges() {
		return getGroupsAsArray('edge');
    }
    function getNodes() {
		return getGroupsAsArray('node');
    }
    function getClusters() {
		return getGroupsAsArray('cluster');
    }
	function get_group(in_element) {
	  var element = in_element;
	  while (element.tagName != 'g') {
	    element = element.parentNode;
	  }
	  return element;
	}
	function highlight_edge(edge_group, color) {
	  var path = get_path(edge_group);
      store_attributes(path, ["stroke", "stroke-width"]);
      path.setAttribute("stroke", color);
      path.setAttribute("stroke-width", "5");
      var arrowHead = edge_group.getElementsByTagName('polygon')[0];
      store_attributes(arrowHead, ["fill", "stroke"]);
      arrowHead.setAttribute("fill", color);
      arrowHead.setAttribute("stroke", color);
	}
	function highlight_node(node_group, color) {
        var nodeShape = get_node_shape(node_group);
        store_attributes(nodeShape, ["stroke", "stroke-width"]);
        nodeShape.setAttribute("stroke", color);
        nodeShape.setAttribute("stroke-width", "5");
	}
    function line_over(evt, nodes) {
        if (frozenNode != null) return;
		var edge_group = get_group(evt.target);
		highlight_edge(edge_group, "yellow");
		highlight_node(getNodeByTitle(nodes[0]), "darkorange");
		highlight_node(getNodeByTitle(nodes[1]), "aqua");
    }
	function get_node_shape(node_group) {
        var nodeShape = node_group.getElementsByTagName('polygon')[0];
		if (!nodeShape) {
			nodeShape = node_group.getElementsByTagName('ellipse')[0];
		}
		return nodeShape
	}
	function restore_edge(edge_group) {
	  var path = get_path(edge_group);
      restore_attributes(path, ["stroke", "stroke-width"]);
      var arrowHead = edge_group.getElementsByTagName('polygon')[0];
      restore_attributes(arrowHead, ["fill", "stroke"]);
	}
	function restore_node(node_group) {
		var nodeShape = get_node_shape(node_group);
        restore_attributes(nodeShape, ["stroke", "stroke-width"]);
    }
    function line_out(evt, nodes) {
      if (frozenNode != null) return;
      var edge_group = evt.target.parentNode.parentNode;
	  restore_edge(edge_group);
      for (i in nodes) {
        var node_group = getNodeByTitle(nodes[i]);
		restore_node(node_group);
      }
    }
    function node_line_over(evt, targetEdges, sourceEdges) {
        if (frozenNode != null) return;
        highlight_node(get_group(evt.target), "yellow");
	    for (i in targetEdges) {
		   var edgeGroup = getEdgeById(targetEdges[i]);
		   highlight_edge(edgeGroup, "darkorange"); 
		   highlight_node(getNodeByTitle(edgeGroup.getAttribute("fromnode")), "darkorange");
		}
	    for (i in sourceEdges) {
		   var edgeGroup = getEdgeById(sourceEdges[i]);
		   highlight_edge(edgeGroup, "aqua"); 
		   highlight_node(getNodeByTitle(edgeGroup.getAttribute("tonode")), "aqua");
		}
    }
    function node_line_out(evt, targetEdges, sourceEdges) {
        if (frozenNode != null) return;
        restore_node(get_group(evt.target));
	    for (i in targetEdges) {
		   var edgeGroup = getEdgeById(targetEdges[i]);
		   restore_edge(edgeGroup); 
		   restore_node(getNodeByTitle(edgeGroup.getAttribute("fromnode")));
		}
	    for (i in sourceEdges) {
		   var edgeGroup = getEdgeById(sourceEdges[i]);
		   restore_edge(edgeGroup); 
		   restore_node(getNodeByTitle(edgeGroup.getAttribute("tonode")));
		}
    }

    var BrowserDetect = {
	init: function () {
		this.browser = this.searchString(this.dataBrowser) || "An unknown browser";
		this.version = this.searchVersion(navigator.userAgent)
			|| this.searchVersion(navigator.appVersion)
			|| "an unknown version";
		this.OS = this.searchString(this.dataOS) || "an unknown OS";
	},
	searchString: function (data) {
		for (var i=0;i<data.length;i++)	{
			var dataString = data[i].string;
			var dataProp = data[i].prop;
			this.versionSearchString = data[i].versionSearch || data[i].identity;
			if (dataString) {
				if (dataString.indexOf(data[i].subString) != -1)
					return data[i].identity;
			}
			else if (dataProp)
				return data[i].identity;
		}
	},
	searchVersion: function (dataString) {
		var index = dataString.indexOf(this.versionSearchString);
		if (index == -1) return;
		return parseFloat(dataString.substring(index+this.versionSearchString.length+1));
	},
	dataBrowser: [
		{
			string: navigator.userAgent,
			subString: "Chrome",
			identity: "Chrome"
		},
		{ 	string: navigator.userAgent,
			subString: "OmniWeb",
			versionSearch: "OmniWeb/",
			identity: "OmniWeb"
		},
		{
			string: navigator.vendor,
			subString: "Apple",
			identity: "Safari",
			versionSearch: "Version"
		},
		{
			prop: window.opera,
			identity: "Opera"
		},
		{
			string: navigator.vendor,
			subString: "iCab",
			identity: "iCab"
		},
		{
			string: navigator.vendor,
			subString: "KDE",
			identity: "Konqueror"
		},
		{
			string: navigator.userAgent,
			subString: "Firefox",
			identity: "Firefox"
		},
		{
			string: navigator.vendor,
			subString: "Camino",
			identity: "Camino"
		},
		{		// for newer Netscapes (6+)
			string: navigator.userAgent,
			subString: "Netscape",
			identity: "Netscape"
		},
		{
			string: navigator.userAgent,
			subString: "MSIE",
			identity: "Explorer",
			versionSearch: "MSIE"
		},
		{
			string: navigator.userAgent,
			subString: "Gecko",
			identity: "Mozilla",
			versionSearch: "rv"
		},
		{ 		// for older Netscapes (4-)
			string: navigator.userAgent,
			subString: "Mozilla",
			identity: "Netscape",
			versionSearch: "Mozilla"
		}
	],
	dataOS : [
		{
			string: navigator.platform,
			subString: "Win",
			identity: "Windows"
		},
		{
			string: navigator.platform,
			subString: "Mac",
			identity: "Mac"
		},
		{
			   string: navigator.userAgent,
			   subString: "iPhone",
			   identity: "iPhone/iPod"
	    },
		{
			string: navigator.platform,
			subString: "Linux",
			identity: "Linux"
		}
	]

};

    