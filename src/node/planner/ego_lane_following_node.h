/*
 * Copyright 2020 Ke Sun
 *
 * Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
 *
 * 1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
 *
 * 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
 *
 * 3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
*/

#pragma once

#include <actionlib/server/simple_action_server.h>
#include <conformal_lattice_planner/EgoPlanAction.h>
#include <node/planner/planning_node.h>

namespace node {

class EgoLaneFollowingNode : public PlanningNode {

private:

  using Base = PlanningNode;
  using This = EgoLaneFollowingNode;

public:

  using Ptr = boost::shared_ptr<This>;
  using ConstPtr = boost::shared_ptr<const This>;

protected:

  mutable ros::Publisher path_pub_;
  mutable actionlib::SimpleActionServer<
    conformal_lattice_planner::EgoPlanAction> server_;

public:

  EgoLaneFollowingNode(ros::NodeHandle& nh) :
    Base(nh),
    server_(nh, "ego_plan", boost::bind(&EgoLaneFollowingNode::executeCallback, this, _1), false) {}

  virtual ~EgoLaneFollowingNode() {}

  virtual bool initialize() override;

protected:

  virtual void executeCallback(
      const conformal_lattice_planner::EgoPlanGoalConstPtr& goal);

}; // End class EgoLaneFollowingNode.

using EgoLaneFollowingNodePtr = EgoLaneFollowingNode::Ptr;
using EgoLaneFollowingNodeConstPtr = EgoLaneFollowingNode::ConstPtr;

} // End namespace node.
