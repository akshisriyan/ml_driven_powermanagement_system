globals [
  total-voltage
  total-load
  house-growth-rate
]

breed [houses house]
houses-own [voltage load]

to setup
  clear-all
  set house-growth-rate 0.02
  create-houses 100 [
    setxy random-xcor random-ycor
    set voltage random-float 240
    set load random-float 10
  ]
  reset-ticks
end

to go
  grow-houses
  update-grid
  export-data
  tick
end

to grow-houses
  if random-float 1 < house-growth-rate [
    create-houses 1 [
      setxy random-xcor random-ycor
      set voltage random-float 240
      set load random-float 10
    ]
  ]
end

to update-grid
  set total-voltage sum [voltage] of houses
  set total-load sum [load] of houses
  ask houses [
    set voltage voltage + random-float 0.5 - 0.25
    set load load + random-float 0.2 - 0.1
  ]
end

to export-data
  file-open "grid_data.csv"
  file-print (word ticks "," total-voltage "," total-load "," count houses)
  file-close
end