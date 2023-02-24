import numpy as np
import pandas as pd

from opentrons import types

metadata = {
    'protocolName': 'HTGAA Robotic Patterning',
    'author': 'HTGAA',
    'source': 'HTGAA 2022',
    'apiLevel': '2.9'
}

def run(protocol):

  ##############################################################################
  ###   Load labware, modules and pipettes
  ##############################################################################

  # Tips
  tips_20ul = protocol.load_labware('opentrons_96_tiprack_20ul', 3, 'Opentrons 20uL Tips')

  # Modules
  temperature_module = protocol.load_module('temperature module gen2', 9)

  # Temperature Module Plate
  temp_plate = temperature_module.load_labware('opentrons_96_aluminumblock_generic_pcr_strip_200ul', label='Cold Plate')

  # Agar Plate
  agar_plate = protocol.load_labware('htgaa_agar_plate', 1, 'Agar Plate')  ## TA MUST CALIBRATE EACH PLATE!

  # Pipettes
  pipette_20ul = protocol.load_instrument("p20_single_gen2", "right", tip_racks=[tips_20ul])


  ##############################################################################
  ###   Configure starting tips 
  ##############################################################################

  pipette_20ul.starting_tip = tips_20ul.well('A1')   ## CHANGE ME

  ##############################################################################
  ###   Patterning
  ##############################################################################

  # Replace the code below with your pattern
  
  # Get the top-center of the plate, make sure the plate was calibrated before running this
  center_location = agar_plate['A1'].top()

  # Choose where to take the colors from
  input_plate = temp_plate

  #Gets the coordinates of my design, so that they can be read into the protocol
  # https://raw.githubusercontent.com/KevinH48264/DNA-Helix-Coordinates/blob/main/dna-coordinates.csv
  # url = 'https://raw.githubusercontent.com/KevinH48264/DNA-Helix-Coordinates/main/dna-coordinates.csv'
  url = 'https://raw.githubusercontent.com/KevinH48264/DNA-Helix-Coordinates/main/2_24%20OpenTron%20Design%20-%20Sheet1%20(3).csv'
  world_coord = pd.read_csv(url)
  data = world_coord
  data.columns = ["x", "y"]

  #Inverts the y-coordinates, else my design is upside-down
  y_inverted = np.amax(data['y'])-data['y']

  #Get min and max x-/y-values from my coordinates
  raw_x_min = np.amin(data['x'])
  raw_x_max = np.amax(data['x'])
  raw_y_min = np.amin(y_inverted)
  raw_y_max = np.amax(y_inverted)


  #Shift data, so that the centerpoint 0/0 is at the center of my design 
  world_coord_x_shifted = data['x']-((raw_x_min + raw_x_max)/2)
  world_coord_y_shifted = y_inverted-((raw_y_min + raw_y_max)/2)

  all_distances_to_center = np.sqrt(np.square(world_coord_x_shifted) + np.square(world_coord_y_shifted));

  world_coord_x_85mm_shifted = 40/np.amax(all_distances_to_center)*world_coord_x_shifted;
  world_coord_y_85mm_shifted = 40/np.amax(all_distances_to_center)*world_coord_y_shifted;

  #Opentron Protocol for a pink microbial earth

  # Get the top-center of the plate, make sure the plate was calibrated before running this
  
  center_location = agar_plate['A1'].top() 

  # color 1
  # cell_well = input_plate['H1'] #Change to location of pink transformands

  # Aspirate
  pipette_20ul.pick_up_tip()

  for i in range(int(len(world_coord_x_85mm_shifted) / 2)):
    if i%20 == 0:
      #pick up more every 20 uL
      aspirate_amount = min(int(len(world_coord_x_85mm_shifted) / 2) - i, 20)
      pipette_20ul.aspirate(aspirate_amount, input_plate['H5'])

    adjusted_location = center_location.move(types.Point(world_coord_x_85mm_shifted[i], world_coord_y_85mm_shifted[i]))
    pipette_20ul.dispense(1, adjusted_location) 
    hover_location = adjusted_location.move(types.Point(z = 2))
    pipette_20ul.move_to(hover_location)

  pipette_20ul.drop_tip()

  # Change color for second dna helix on the right, missing filled in bottom
  # Aspirate
  pipette_20ul.pick_up_tip()

  for i in range(int(len(world_coord_x_85mm_shifted) / 2), int(len(world_coord_x_85mm_shifted)) - 22):
    if i == int(len(world_coord_x_85mm_shifted) / 2):
      pipette_20ul.aspirate(20 - (int(len(world_coord_x_85mm_shifted) / 2) % 20), input_plate['H7'])

    elif i%20 == 0:
      #pick up more every 20 uL
      pipette_20ul.aspirate(min(int(len(world_coord_x_85mm_shifted)) - 22 - i, 20), input_plate['H7'])

    adjusted_location = center_location.move(types.Point(world_coord_x_85mm_shifted[i], world_coord_y_85mm_shifted[i]))
    pipette_20ul.dispense(1, adjusted_location) 
    hover_location = adjusted_location.move(types.Point(z = 2))
    pipette_20ul.move_to(hover_location)
  
  pipette_20ul.drop_tip()

  # Mix the middle with some blue to make some red on the right top side, and blue on the bottom right side
  # Aspirate
  pipette_20ul.pick_up_tip()

  for i in range((int(len(world_coord_x_85mm_shifted) / 2) + 40), int(len(world_coord_x_85mm_shifted))):
    if i == (int(len(world_coord_x_85mm_shifted) / 2) + 40):
      pipette_20ul.aspirate(20 - ((int(len(world_coord_x_85mm_shifted) / 2) + 40) % 20), input_plate['H6'])

    elif i%20 == 0:
      #pick up more every 20 uL
      pipette_20ul.aspirate(20, input_plate['H6'])

    adjusted_location = center_location.move(types.Point(world_coord_x_85mm_shifted[i], world_coord_y_85mm_shifted[i]))
    pipette_20ul.dispense(1, adjusted_location) 
    hover_location = adjusted_location.move(types.Point(z = 2))
    pipette_20ul.move_to(hover_location)


  pipette_20ul.drop_tip()