import React, { useEffect, useRef, useState } from "react";
import { useQuery, gql } from '@apollo/client';
import * as d3 from "d3";

const GET_HISTORICAL_DATA = gql`
  query GetHistoricalData($startDate: String!, $endDate: String!) {
    getMSTRHistoricalData(startDate: $startDate, endDate: $endDate) {
      date
      close
    }
  }
`;

const width = 1200;
const height = 500;

const LPPLSChart = () => {
  const { loading, error, data } = useQuery(GET_HISTORICAL_DATA, {
    variables: {
      startDate: '2022-01-01',
      endDate: '2023-05-31'
    },
  });

  const svgRef = useRef();

  const criticalTimings = {
    t1: new Date('2022-01-01'),
    t2: new Date('2023-05-31'),
    tc: new Date('2022-07-01')
  };

  useEffect(() => {
    if (loading || error || !data) return;



    const priceData = data.getMSTRHistoricalData.map(d => ({
      date: new Date(d.date),
      price: d.close,
      logPrice: Math.log(d.close)
    }));

    // Chart Dimensions
    const margin = { top: 40, right: 40, bottom: 50, left: 60 };

    // Clear previous SVG
    const svg = d3.select(svgRef.current);
    svg.selectAll("*").remove();

    // Scales
    const xScale = d3
      .scaleTime()
      .domain(d3.extent(priceData, d => d.date))
      .range([margin.left, width - margin.right]);

    const yScale = d3
      .scaleLinear()
      .domain([d3.min(priceData, d => d.logPrice) * 0.9, d3.max(priceData, d => d.logPrice) * 1.1])
      .range([height - margin.bottom, margin.top]);

    // Chart Group
    const chartGroup = svg.append("g");

    // Draw Log Price Line (Black)
    const priceLine = d3
      .line()
      .x(d => xScale(d.date))
      .y(d => yScale(d.logPrice))
      .curve(d3.curveMonotoneX);

    chartGroup
      .append("path")
      .datum(priceData)
      .attr("fill", "none")
      .attr("stroke", "black")
      .attr("stroke-width", 2)
      .attr("d", priceLine);

     // Draw LPPLS Fit Line (Blue)
      const fitLine = d3
        .line()
        .x((d) => xScale(new Date(d.date)))
        .y((d) => yScale(d.lpplsFit))
        .curve(d3.curveMonotoneX);
  
      chartGroup
        .append("path")
        .datum(priceData)
        .attr("fill", "none")
        .attr("stroke", "blue")
        .attr("stroke-width", 2)
        .attr("d", fitLine);
  
      // Draw Vertical Lines for Critical Timings
      const verticalLines = [
        { date: criticalTimings.t1, color: "green", label: "t₁ (Start)" },
        { date: criticalTimings.t2, color: "orange", label: "t₂ (End)" },
        { date: criticalTimings.tc, color: "red", label: "tₚ (Critical Time)" },
      ];
  
      verticalLines.forEach(({ date, color, label }) => {
        if (!date) return;
  
        const xPos = xScale(new Date(date));
        chartGroup
          .append("line")
          .attr("x1", xPos)
          .attr("x2", xPos)
          .attr("y1", margin.top)
          .attr("y2", height - margin.bottom)
          .attr("stroke", color)
          .attr("stroke-width", 2)
          .attr("stroke-dasharray", "4,4");
  
        chartGroup
          .append("text")
          .attr("x", xPos + 5)
          .attr("y", margin.top + 10)
          .attr("fill", color)
          .attr("font-size", "12px")
          .text(label);
      });

    // Add Axes
    const xAxis = d3.axisBottom(xScale).tickFormat(d3.timeFormat("%Y-%m"));
    svg.append("g")
      .attr("transform", `translate(0, ${height - margin.bottom})`)
      .call(xAxis);

    const yAxis = d3.axisLeft(yScale);
    svg.append("g")
      .attr("transform", `translate(${margin.left}, 0)`)
      .call(yAxis);

    // Add Labels
    svg.append("text")
      .attr("x", width / 2)
      .attr("y", height - 10)
      .attr("text-anchor", "middle")
      .attr("font-size", "14px")
      .text("Date");

    svg.append("text")
      .attr("x", -height / 2)
      .attr("y", 15)
      .attr("text-anchor", "middle")
      .attr("transform", "rotate(-90)")
      .attr("font-size", "14px")
      .text("Log Price");

    // Add Legend
    const legend = svg.append("g").attr("transform", `translate(${width - 150}, 30)`);
    const legendItems = [
      { color: "black", text: "Log Price" },
      { color: "blue", text: "LPPLS Fit" },
      { color: "green", text: "t₁ (Start)" },
      { color: "orange", text: "t₂ (End)" },
      { color: "red", text: "tₚ (Critical Time)" },
    ];

    legendItems.forEach((item, index) => {
      legend.append("line")
        .attr("x1", 0)
        .attr("x2", 20)
        .attr("y1", index * 15)
        .attr("y2", index * 15)
        .attr("stroke", item.color)
        .attr("stroke-width", 2);

      legend.append("text")
        .attr("x", 30)
        .attr("y", index * 15 + 5)
        .attr("fill", "black")
        .attr("font-size", "12px")
        .text(item.text);
    });

  }, [loading, error, data]);

  if (loading) return <p>Loading...</p>;
  if (error) return <p>Error: {error.message}</p>;

  return <svg ref={svgRef} width={width} height={height} />;
};

export default LPPLSChart;