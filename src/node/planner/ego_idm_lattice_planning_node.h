/*
 * Copyright [2019] [Ke Sun]
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

#pragma once

#include <boost/smart_ptr.hpp>
#include <boost/optional.hpp>
#include <actionlib/server/simple_action_server.h>

#include <conformal_lattice_planner/EgoPlanAction.h>
#include <planner/common/vehicle_speed_planner.h>
#include <planner/idm_lattice_planner/idm_lattice_planner.h>
#include <node/planner/planning_node.h>

namespace node {

class EgoIDMLatticePlanningNode : public PlanningNode {

private:

  using Base = PlanningNode;
  using This = EgoIDMLatticePlanningNode;

public:

  using Ptr = boost::shared_ptr<This>;
  using ConstPtr = boost::shared_ptr<const This>;

protected:

  boost::shared_ptr<planner::IDMLatticePlanner> path_planner_ = nullptr;
  boost::shared_ptr<planner::VehicleSpeedPlanner> speed_planner_ = nullptr;

  mutable ros::Publisher path_pub_;
  mutable ros::Publisher conformal_lattice_pub_;
  mutable ros::Publisher waypoint_lattice_pub_;

  mutable actionlib::SimpleActionServer<
    conformal_lattice_planner::EgoPlanAction> server_;

public:

  EgoIDMLatticePlanningNode(ros::NodeHandle& nh) :
    Base(nh),
    server_(
        nh,
        "ego_plan",
        boost::bind(&EgoIDMLatticePlanningNode::executeCallback, this, _1),
        false) {}

  virtual ~EgoIDMLatticePlanningNode() {}

  virtual bool initialize() override;

protected:

  virtual void executeCallback(
      const conformal_lattice_planner::EgoPlanGoalConstPtr& goal);

}; // End class EgoIDMLatticePlanningNode.

using EgoIDMLatticePlanningNodePtr = EgoIDMLatticePlanningNode::Ptr;
using EgoIDMLatticePlanningNodeConstPtr = EgoIDMLatticePlanningNode::ConstPtr;

} // End namespace node.
